# AgentDbg Website Strategy

*Last updated: 2026-04-05*

## 1) Strategic Objective
Build a website that converts skeptical agent developers into first-time users by proving one thing quickly:

**AgentDbg helps you understand and stop bad agent behavior in minutes, locally.**

Primary conversion: `pip install agentdbg`  
Secondary conversion: open docs / examples, star GitHub.

## 2) Positioning
### Core Position
AgentDbg is a **local-first debugger for AI agents**.  
It is **not** an observability platform.

### Positioning Statement
For Python developers building agent workflows that behave unpredictably, AgentDbg is the debugging tool that shows exactly what happened in a run and can stop runaway loops before they burn budget, without sending trace data to the cloud.

### Message Boundaries
Use:
- debugger
- timeline
- run
- loop warning
- guardrails
- local-first
- fix fast

Avoid:
- observability
- monitoring
- dashboards and alerts
- production telemetry platform

## 3) Audience Segments
### Segment A: Solo Builder (Primary)
- Context: building fast, limited time, limited budget.
- Need: immediate visibility and protection against loops.
- Trigger phrase: "I don't know what my agent is doing."

### Segment B: Startup Engineer (Secondary)
- Context: small team shipping internal/external agent features.
- Need: reproducible debugging evidence and lower regression risk.
- Trigger phrase: "It worked yesterday."

### Segment C: AI Infra Lead (Future)
- Context: planning CI/reliability workflows.
- Need: path to compare/replay/assertions, but local debugger first.

## 4) Value Pillars (site narrative order)
1. **See what happened:** timeline of LLM calls, tool calls, errors, and state updates.
2. **Stop runaway runs:** guardrails abort loops and cap breaches.
3. **Keep data local:** no cloud account or telemetry requirement.
4. **Adopt quickly:** `@trace` + `agentdbg view` in under 10 minutes.
5. **Use your stack:** framework-agnostic core + optional integrations.

## 5) Homepage Narrative Arc
1. Hero: debugger identity + local-first trust + install CTA.
2. Problem: print logs and cloud traces are slow/noisy for development-time debugging.
3. Product mechanism: timeline and event evidence.
4. Guardrails wedge: active prevention, not just passive tracing.
5. Integrations: LangChain/LangGraph, OpenAI Agents SDK, CrewAI.
6. Workflow clarity: install -> instrument -> run -> view.
7. Final CTA: install now + docs/examples.

## 6) CTA Strategy
### Primary CTA labels
- `Install AgentDbg`
- `Get Started in 5 Minutes`

### Secondary CTA labels
- `View Docs`
- `See Example Runs`
- `Star on GitHub`

### CTA Placement
- Hero (primary + secondary)
- After guardrails section
- Final section above footer

## 7) Proof Strategy (current-stage appropriate)
Use proof that exists today:
- clear architecture story (local-first, no cloud required)
- concrete guardrail behavior
- integrations shipped
- test and release discipline
- demos/GIFs from docs

Do not overstate:
- enterprise readiness
- production monitoring capabilities
- large-customer claims

## 8) Go-to-Market Alignment
The website should support:
- social posts and demos (clear hero + GIF-ready sections)
- docs entry (tutorial and integration pathways)
- early adopter trust (transparent scope and boundaries)

## 9) Success Metrics for This Site Version
### Activation metrics
- CTR on `Install AgentDbg`
- README/docs clickthrough from homepage
- % of visitors reaching quickstart section

### Trust metrics
- Scroll depth to local-first + guardrails sections
- CTR on integrations section

### Behavior metric
- Ratio of `Install` clicks to raw homepage visits

