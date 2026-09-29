import argparse
import json
import sys

import httpx


def main() -> int:
    parser = argparse.ArgumentParser(description="Exercise the live app and Hindsight retain/recall path.")
    parser.add_argument("--app-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    client = httpx.Client(base_url=args.app_url, timeout=120)

    health = client.get("/api/health").raise_for_status().json()
    if not health["hindsight_connected"]:
        raise RuntimeError("Hindsight is not reachable; start scripts/run_hindsight.ps1 first.")

    current = {
        "merchant": "Store B",
        "processor": "Stripe",
        "error": "timeout",
        "amount_inr": 3800,
    }
    before = client.post("/api/analyze", json={**current, "mode": "without"}).raise_for_status().json()
    assert before["memory_used"] is False
    assert before["evidence"] is None
    print("WITHOUT MEMORY:", before["guidance"])

    prior = {
        "merchant": "Store A",
        "processor": "Stripe",
        "error": "timeout",
        "amount_inr": 4500,
        "resolution": "Payment was successfully routed through another processor.",
    }
    retained = client.post("/api/incidents/retain", json=prior).raise_for_status().json()
    assert retained["retained"] is True
    print("RETAINED IN HINDSIGHT:", retained["content"])

    after = client.post("/api/analyze", json={**current, "mode": "with"}).raise_for_status().json()
    evidence = json.dumps(after["evidence"], ensure_ascii=False).lower()
    if "another processor" not in evidence and "different processor" not in evidence:
        raise AssertionError(f"Hindsight recall did not return the expected prior resolution: {evidence}")
    if not after["memory_used"]:
        raise AssertionError("The app did not mark the returned Hindsight memory as used.")
    print("HINDSIGHT RECALL EVIDENCE:", evidence)
    print("WITH HINDSIGHT:", after["guidance"])
    print("Smoke flow passed against the running Hindsight API and PaymentOps app.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Smoke flow failed: {exc}", file=sys.stderr)
        raise
