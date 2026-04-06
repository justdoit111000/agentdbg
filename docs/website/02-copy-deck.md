# AgentDbg Website Copy Deck

*Last updated: 2026-04-05*

## 1) Homepage Copy

### Hero
**Headline (Option A):**  
Debug AI agents locally, step by step.

**Headline (Option B):**  
See exactly what your agent did.

**Headline (Option C):**  
Stop guessing. Start debugging agent runs.

**Subheadline:**  
AgentDbg is the local-first debugger for AI agents. Add `@trace`, run your workflow, and inspect a clean timeline of LLM calls, tool calls, errors, and loop warnings in minutes.

**Primary CTA:**  
Install AgentDbg

**Secondary CTA:**  
Get Started in 5 Minutes

**Hero micro-proof:**  
No cloud. No accounts. No telemetry. Everything stays on your machine.

### Problem Section
**Section title:**  
Agent failures are expensive when they're opaque.

**Body copy:**  
Most agent debugging still happens through print statements, scattered logs, and reruns that do not reproduce the same behavior. By the time you realize a run is stuck, you've already lost time and budget.

**Pain bullets:**
- "Why did it call that tool?"
- "It worked yesterday."
- "Why is it still running?"

### Solution Section
**Section title:**  
One run. One timeline. Clear evidence.

**Body copy:**  
AgentDbg records each run as a chronological event stream, so you can inspect what happened without reconstructing context from multiple tools.

**Feature bullets:**
- `LLM_CALL` with model, prompt, response, usage
- `TOOL_CALL` with args, results, status
- `ERROR` with stack trace
- `LOOP_WARNING` with repeated-pattern evidence

### Guardrails Section
**Section title:**  
Stop runaway runs before they burn budget.

**Body copy:**  
Guardrails can automatically abort a run when it loops or crosses your configured limits for calls, events, or duration. AgentDbg still records the full trail to the abort point so you can fix the root cause immediately.

**Code snippet copy block:**
```python
@trace(stop_on_loop=True, max_llm_calls=50, max_duration_s=120)
def run_agent():
    ...
```

### Integrations Section
**Section title:**  
Use your current stack.

**Body copy:**  
The core stays framework-agnostic, and integrations are optional thin adapters.

**Integration labels:**
- LangChain / LangGraph
- OpenAI Agents SDK
- CrewAI

### Quickstart Section
**Section title:**  
From install to first useful timeline in under 10 minutes.

**Step copy:**
1. `pip install agentdbg`
2. Add `@trace` to your run entrypoint
3. Run your agent
4. Run `agentdbg view`

### FAQ Section
**Q: Is this an observability platform?**  
No. AgentDbg is built for development-time debugging of single runs, not production monitoring dashboards.

**Q: Does any data leave my machine?**  
No. Traces are stored locally by default.

**Q: Do I need to adopt a specific framework?**  
No. Core instrumentation is framework-agnostic.

**Q: Can this prevent expensive loops?**  
Yes. Guardrails can stop looping or over-limit runs automatically.

### Final CTA Section
**Headline:**  
Debug your next agent run with evidence, not guesswork.

**Primary CTA:**  
Install AgentDbg

**Secondary CTA:**  
View Documentation

---

## 2) Guardrails Page Copy

**Page title:**  
Guardrails: stop runaway agent runs early

**Intro:**  
Guardrails are optional development-time safety rails that stop agent runs when behavior crosses your thresholds.

**Key outcomes:**
- Abort loops early with `stop_on_loop`
- Cap LLM calls, tool calls, events, and duration
- Preserve full run evidence up to abort point

**Primary CTA:**  
Implement Guardrails

---

## 3) Integrations Index Page Copy

**Page title:**  
Integrations for common Python agent stacks

**Intro:**  
Use AgentDbg directly in custom code, or connect it to your existing framework via optional integrations.

**Cards:**
- **LangChain / LangGraph**  
Callback handler integration for LLM and tool lifecycle events.
- **OpenAI Agents SDK**  
Tracing processor integration for generation spans, function calls, and handoffs.
- **CrewAI**  
Execution hook adapter for LLM and tool call visibility.

**Primary CTA:**  
See Integration Setup

---

## 4) CTA Variants for Testing

### Install CTA variants
- Install AgentDbg
- Start Debugging Locally
- Get Timeline Debugging

### Secondary CTA variants
- Run the Quickstart
- See a Demo Run
- Explore Docs

### Hero subheadline variants
- "A local-first debugger that shows exactly what your agent did, then helps you stop runaway behavior before it gets expensive."
- "Get a clean run timeline with LLM calls, tool calls, errors, and loop warnings in minutes."
- "Debug agent behavior with structured evidence, not scattered logs."

---

## 5) Metadata Drafts

### Homepage
**Meta title:**  
AgentDbg | Local-first debugger for AI agents

**Meta description:**  
Debug AI agent runs locally with a step-by-step timeline of LLM calls, tool calls, errors, and loop warnings. Stop runaway runs with built-in guardrails.

### Guardrails page
**Meta title:**  
Guardrails | AgentDbg

**Meta description:**  
Configure stop-on-loop and run caps to abort runaway agent behavior while preserving full debugging evidence.

### Integrations page
**Meta title:**  
Integrations | AgentDbg

**Meta description:**  
Connect AgentDbg with LangChain, LangGraph, OpenAI Agents SDK, and CrewAI using optional adapters.

