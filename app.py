from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Literal

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")

HINDSIGHT_URL = os.getenv("HINDSIGHT_URL", "http://127.0.0.1:8888").rstrip("/")
HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY", "")
HINDSIGHT_BANK = os.getenv("HINDSIGHT_BANK", "paymentops-demo")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

app = FastAPI(title="PaymentOps Memory Agent", version="0.1.0")


class Incident(BaseModel):
    merchant: str = Field(min_length=1, max_length=100)
    processor: str = Field(min_length=1, max_length=80)
    error: str = Field(min_length=1, max_length=120)
    amount_inr: int = Field(gt=0, le=10_000_000)


class PreviousIncident(Incident):
    resolution: str = Field(min_length=5, max_length=1000)


class AnalysisRequest(Incident):
    mode: Literal["without", "with"]


def hindsight_client():
    try:
        from hindsight_client import Hindsight
    except ImportError as exc:
        raise HTTPException(
            status_code=503,
            detail="Install the project requirements to enable the Hindsight client.",
        ) from exc
    options = {"base_url": HINDSIGHT_URL}
    if HINDSIGHT_API_KEY:
        options["api_key"] = HINDSIGHT_API_KEY
    return Hindsight(**options)


def as_plain_data(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if hasattr(value, "dict"):
        return value.dict()
    if isinstance(value, (list, tuple)):
        return [as_plain_data(item) for item in value]
    if isinstance(value, dict):
        return {str(key): as_plain_data(item) for key, item in value.items()}
    if hasattr(value, "__dict__"):
        return {key: as_plain_data(item) for key, item in vars(value).items() if not key.startswith("_")}
    return value


def searchable_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(as_plain_data(value), ensure_ascii=False, default=str)


def recalled_memory_text(value: Any) -> str:
    data = as_plain_data(value)
    if not isinstance(data, dict):
        return ""
    chunks = data.get("chunks") or {}
    excerpts = []
    for result in data.get("results") or []:
        if not isinstance(result, dict):
            continue
        if result.get("text"):
            excerpts.append(str(result["text"]))
        chunk_id = result.get("chunk_id")
        chunk = chunks.get(chunk_id) if chunk_id else None
        if isinstance(chunk, dict) and chunk.get("text"):
            excerpts.append(str(chunk["text"]))
    return "\n".join(dict.fromkeys(excerpts))


def generic_guidance(incident: Incident) -> str:
    return (
        f"A {incident.error} was reported by {incident.processor} for {incident.merchant}. "
        "Check the processor status and request logs, verify whether the payment reached a "
        "terminal state, and avoid an immediate duplicate retry until the original attempt "
        "is reconciled. No prior incident was consulted for this analysis."
    )


def memory_guidance(incident: Incident, evidence: str) -> str:
    lowered = evidence.lower()
    if not evidence or incident.processor.lower() not in lowered or incident.error.lower() not in lowered:
        return (
            f"Hindsight returned no prior incident for this {incident.processor} "
            f"{incident.error}. Check processor status and request logs, reconcile the "
            "original attempt before retrying, and retain the outcome after investigation."
        )

    prior_resolution = "another processor" if "another processor" in lowered or "different processor" in lowered else "a prior resolution"
    return (
        f"Hindsight recalled a previous incident relevant to this {incident.processor} "
        f"{incident.error}. The recalled experience records that it was resolved through "
        f"{prior_resolution}. Compare the current processor response and request logs with "
        "that incident, confirm the original attempt's final state, and investigate "
        "processor-specific timeout behavior before retrying through the same processor. "
        "The recalled incident is guidance, not a guarantee that the same action will work."
    )


def optional_llm_guidance(incident: Incident, recalled: Any, fallback: str) -> tuple[str, str]:
    if not OPENAI_API_KEY:
        return fallback, "Deterministic guidance using current incident and Hindsight evidence"
    try:
        from openai import OpenAI

        result = OpenAI(api_key=OPENAI_API_KEY).chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a payment operations investigation assistant. Use only the "
                        "synthetic current incident and recalled memory provided. Distinguish "
                        "past evidence from suggestions; do not claim a payment was processed."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Current synthetic incident: {incident.model_dump_json()}\n"
                        f"Hindsight recall: {searchable_text(recalled)}\n"
                        f"Fallback guidance: {fallback}"
                    ),
                },
            ],
        )
        content = result.choices[0].message.content
        if content:
            return content, f"{OPENAI_MODEL} with Hindsight recall"
    except Exception:
        return fallback, "Deterministic guidance (configured LLM request failed)"
    return fallback, "Deterministic guidance using current incident and Hindsight evidence"


@app.get("/")
def home():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/api/health")
def health():
    try:
        headers = {"Authorization": f"Bearer {HINDSIGHT_API_KEY}"} if HINDSIGHT_API_KEY else None
        response = httpx.get(f"{HINDSIGHT_URL}/health", headers=headers, timeout=2.0)
        connected = response.is_success
        detail = "connected" if connected else f"Hindsight returned HTTP {response.status_code}"
    except httpx.HTTPError:
        connected = False
        detail = "Hindsight is not reachable"
    return {
        "app": "ready",
        "hindsight_connected": connected,
        "hindsight_url": HINDSIGHT_URL,
        "bank_id": HINDSIGHT_BANK,
        "agent_mode": "OpenAI optional" if OPENAI_API_KEY else "deterministic",
        "detail": detail,
    }


@app.post("/api/incidents/retain")
def retain_incident(incident: PreviousIncident):
    content = (
        "Synthetic payment incident experience. "
        f"Merchant: {incident.merchant}. Processor: {incident.processor}. "
        f"Error: {incident.error}. Amount: INR {incident.amount_inr}. "
        f"Resolution: {incident.resolution}"
    )
    client = hindsight_client()
    try:
        result = client.retain(bank_id=HINDSIGHT_BANK, content=content, retain_async=False)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Hindsight retain failed: {exc}") from exc
    finally:
        client.close()
    return {"retained": True, "bank_id": HINDSIGHT_BANK, "content": content, "hindsight_result": as_plain_data(result)}


@app.post("/api/analyze")
def analyze(request: AnalysisRequest):
    incident = Incident(**request.model_dump(exclude={"mode"}))
    if request.mode == "without":
        return {
            "mode": "without",
            "incident": incident.model_dump(),
            "guidance": generic_guidance(incident),
            "evidence": None,
            "memory_used": False,
            "agent": "Deterministic baseline; Hindsight was not queried",
        }

    query = (
        f"Prior payment incident experience involving processor {incident.processor} "
        f"and error {incident.error}. What resolution and investigation outcome were recorded?"
    )
    client = hindsight_client()
    try:
        recalled = client.recall(
            bank_id=HINDSIGHT_BANK,
            query=query,
            include_chunks=True,
            max_chunk_tokens=1500,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Hindsight recall failed: {exc}") from exc
    finally:
        client.close()
    memory_text = recalled_memory_text(recalled)
    memory_used = bool(
        memory_text
        and incident.processor.lower() in memory_text.lower()
        and incident.error.lower() in memory_text.lower()
    )
    fallback = memory_guidance(incident, memory_text)
    guidance, agent = optional_llm_guidance(incident, recalled if memory_used else {"results": []}, fallback)
    return {
        "mode": "with",
        "incident": incident.model_dump(),
        "guidance": guidance,
        "evidence": as_plain_data(recalled),
        "memory_used": memory_used,
        "agent": agent,
        "query": query,
    }
