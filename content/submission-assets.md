# Submission Assets

## LinkedIn Post

Payment incidents do not become operational knowledge by being summarized once.
They become useful when a later investigation can retrieve the outcome.

- Built a local PaymentOps agent with real Hindsight `retain` and `recall` calls.
- Before memory: Store B gets generic Stripe timeout checks.
- After memory: Hindsight recalls Store A's alternate-processor resolution and changes the investigation guidance.
- The UI exposes the returned memory evidence beside the response.
- Synthetic data only; deterministic wording by default; no payment processing or benchmark claims.

Project repository: [PROJECT_GITHUB_URL]

#Hindsight #AgentMemory #AIAgents #PaymentOps

Character count including the repository placeholder: under 800. Replace the placeholder after publishing the project repository.

## LinkedIn Comments

First comment:

Article: [ARTICLE_URL]

Second comment:

Hindsight: https://github.com/vectorize-io/hindsight

## Three-Minute Team Video Script

### 0:00–0:30 | Introduction

“We built PaymentOps Memory Agent to show what changes when an incident investigation can remember a previous outcome. This is a local prototype using synthetic payment incidents. It does not connect to Stripe or process a payment. The important part is visible: a stateless baseline, a real Hindsight memory call, and the evidence that comes back.”

### 0:30–1:00 | Problem Without Memory

“Here is Store B: Stripe, timeout, INR 3,800. I’ll select Analyze without memory. The response recommends checking processor status and request logs, and reconciling the attempt before retrying. That is sensible, but generic. This path does not call Hindsight, so it cannot know that Store A had a similar failure before.”

### 1:00–2:30 | Live Demonstration

“Now I’ll record that earlier synthetic incident. Store A had a Stripe timeout for INR 4,500. The resolution says the payment was successfully routed through another processor. I’ll select Retain incident in Hindsight. The UI shows the exact experience we sent to the `paymentops-demo` bank.

“Now I’ll analyze the same Store B incident with Hindsight. The app sends a recall query for previous Stripe timeout outcomes. Here is the response payload returned by Hindsight; we can inspect the merchant, processor, error, and resolution rather than treating memory as a hidden prompt.

“The guidance now recommends comparing the processor response with the prior case and investigating processor-specific timeout behavior before retrying through the same processor. The memory changes the investigation context. It does not automatically route or retry a payment. If Hindsight returns no matching memory, the app says so and keeps the guidance generic.”

### 2:30–3:00 | Wrap-Up

“This prototype uses Hindsight for real persistent retain and recall. To keep setup credential-free, it retains raw chunks and uses deterministic response wording by default; it does not claim LLM-based learning or benchmarked retrieval quality. The result is a small, inspectable example of how an agent can reuse an earlier payment investigation. Next, we would test retrieval across a wider synthetic incident set before drawing conclusions about operational impact.”

## Recording Shot List

1. Show the app at `http://127.0.0.1:8000`; keep the “Synthetic incident data only” label and Hindsight connection status visible.
2. Show Store B / Stripe / timeout / INR 3,800. Click **Analyze without memory** and hold on the baseline panel.
3. Enter or confirm Store A / Stripe / timeout / INR 4,500 and the alternate-processor resolution. Click **Retain incident in Hindsight**; show the retained text and success toast.
4. Return focus to the Store B incident and click **Analyze with Hindsight**.
5. Hold on **What Hindsight recalled** so the audience can read the returned evidence. If needed, zoom the page to 110% and crop the browser chrome.
6. Show the two guidance panels together and point out the added processor-specific investigation suggestion.
7. Finish on the architecture poster and state that no payment was processed.

## Exact Demo Commands and Sequence

In PowerShell window 1, from the project directory:

```powershell
.\.venv\Scripts\Activate.ps1
.\scripts\run_hindsight.ps1
```

In PowerShell window 2:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000` and complete shots 1–6 above. For a scripted API pass against those running services:

```powershell
python scripts\smoke_demo.py
```

The first Hindsight boot downloads its configured ONNX embedding model. Start Hindsight before recording so the model is already available.

## Five YouTube Title Options

1. How Hindsight Remembers a Payment Timeout Investigation
2. A PaymentOps Agent With Persistent Hindsight Memory
3. From Generic Stripe Timeout Advice to Recalled Incident Evidence
4. Hindsight Retain and Recall in a Payment Incident Agent
5. Building a Memory-Aware Payment Investigation With FastAPI

## Poster / Architecture Visual

Use [`assets/architecture.svg`](../assets/architecture.svg) as the 16:9 visual. It contains the required title and subtitle and shows the actual implemented flow:

**Payment failure → PaymentOps agent → Hindsight retain/recall → recalled incident evidence → operator-reviewed guidance**

Visual direction: light gray-green background; deep green and soft green for the agent and Hindsight; amber for the baseline. Keep the synthetic INR 3,800 current incident and INR 4,500 retained incident legible. Keep the footer limitation: “Synthetic incidents · Hindsight chunks mode · Deterministic guidance by default · Optional LLM wording.”

## YouTube Thumbnail

Use [`assets/thumbnail.svg`](../assets/thumbnail.svg) at 1280×720 (16:9). The primary text is “PAYMENT AGENT THAT REMEMBERS”; secondary text is “Hindsight Memory.” The left-to-right visual uses the current Stripe timeout, a recalled Store A resolution, and the resulting investigation suggestion. The footer explicitly says the events are synthetic and no payment is processed.

## Screenshot Recommendations

- **Project UI:** capture the full browser viewport at 1440×900 with both baseline and memory-aware panels visible.
- **Before-memory response:** crop the Store B form and baseline panel after the first analysis, before retaining Store A.
- **After-memory response:** crop the memory-aware panel and returned recall evidence after Hindsight recall.
- **Retain/recall proof:** crop the terminal output from `python scripts\smoke_demo.py` alongside the relevant `app.py` client calls; keep the API response readable and avoid showing environment secrets.
- **Architecture:** export or display `assets/architecture.svg` as PNG for article platforms that do not embed SVG.
- **Optional team visual:** use a real team photo only with team consent; it is not needed to explain the implementation.

Capture UI/code in PNG. Keep code crops tight around the Hindsight `retain` and `recall` calls. Do not use an unrun mock screenshot as proof of the Hindsight path.

## Final Submission Checklist

- [ ] Start Hindsight with `scripts/run_hindsight.ps1` and verify the status in the UI.
- [ ] Run the baseline before retaining the prior incident.
- [ ] Retain the synthetic Store A experience and show the submitted text.
- [ ] Recall for Store B and keep the actual Hindsight evidence visible.
- [ ] Run `python scripts\smoke_demo.py` and preserve its actual output for review.
- [ ] Capture genuine app and Hindsight evidence screenshots; do not include credentials.
- [ ] Publish the project repository and replace `[PROJECT_GITHUB_URL]` in the post.
- [ ] Publish the article and replace `[ARTICLE_URL]` in the first comment.
- [ ] Keep the limitations visible: synthetic data, chunk retain mode, deterministic default guidance, no processor integration, and no retrieval benchmark.
