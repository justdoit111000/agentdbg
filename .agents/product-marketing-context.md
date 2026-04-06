# Product Marketing Context

*Last updated: 2026-04-05*

## Product Overview
**One-liner:**  
AgentDbg is a local-first debugger for AI agents.

**What it does:**  
AgentDbg captures structured evidence from a single agent run and shows it as a clean, chronological timeline in a local UI. Developers can inspect LLM calls, tool calls, errors, state updates, and loop warnings in one place. Guardrails can also stop runaway runs mid-execution so debugging sessions do not turn into cost incidents.

**Product category:**  
Developer tooling for agent debugging (not observability).

**Product type:**  
Open-source Python devtool (local-only today), with future team/CI workflows.

**Business model:**  
Free local debugger now; potential paid CI and team debugging workflows later.

## Target Audience
**Target companies:**  
Indie builders, startups, and product teams building AI agent workflows in Python.

**Decision-makers:**  
Founder-engineers, AI/product engineers, early infra/platform engineers.

**Primary use case:**  
Understand exactly what an agent did, why it failed or looped, and fix it quickly.

**Jobs to be done:**
- Diagnose agent loops and repeated tool behavior before costs escalate.
- Debug tool-call failures (bad args, schema mismatches, flaky integrations).
- Compare expected vs actual run behavior after prompt/tool changes.

**Use cases:**
- Local development while iterating on multi-step agent flows.
- Investigating non-deterministic failures that are hard to reproduce.
- Demoing and validating framework integrations (LangChain, OpenAI Agents SDK, CrewAI).

## Personas
| Persona | Cares about | Challenge | Value we promise |
|---------|-------------|-----------|------------------|
| Solo builder (primary user) | Shipping quickly, low setup cost, no vendor lock-in | Debugging is guesswork; loops waste time and money | Install fast, add `@trace`, get immediate timeline clarity locally |
| Startup engineer (champion) | Team velocity, reliability, predictable behavior | Hard to isolate regressions and explain failures to teammates | Structured evidence of exactly what happened in each run |
| Technical lead / infra engineer (future buyer) | Repeatable quality gates, CI confidence | Manual debugging does not scale across PRs/releases | Path from local debugging to compare/replay/CI assertions |

## Problems & Pain Points
**Core problem:**  
Agent behavior is often opaque, non-deterministic, and expensive when it fails.

**Why alternatives fall short:**
- Print statements and scattered logs are noisy and incomplete.
- Cloud-first tracing tools add setup/account friction for local debugging.
- Many tools show what happened after the fact but do not actively stop runaway runs.

**What it costs them:**  
Lost engineering time, delayed releases, and avoidable API spend from loops/retries.

**Emotional tension:**  
"I don't really know what my agent is doing."

## Competitive Landscape
**Direct:**  
LangSmith, Langfuse, Phoenix, OpenAI built-in tracing. Strong for broader tracing/monitoring ecosystems, less focused on local-first debugger workflow and active prevention.

**Secondary:**  
Manual logs, print debugging, ad-hoc dashboards. Flexible but unstructured and slow to reason through.

**Indirect:**  
Avoiding agentic patterns entirely or over-constraining behavior to reduce debugging risk.

## Differentiation
**Key differentiators:**
- Local-first by default: no cloud backend, no account, no telemetry.
- Debugger mental model: single-run timeline with step-by-step evidence.
- Active prevention: stop-on-loop and run caps stop damage mid-run.
- Framework-agnostic core with optional thin integrations.

**How we do it differently:**  
We optimize for development-time clarity and speed to first insight, not production observability breadth.

**Why that's better:**  
Developers get useful debugging evidence in minutes and can fix issues immediately with lower operational overhead.

**Why customers choose us:**  
Fast setup, high trust, practical debugging workflow, and concrete protection against runaway agent behavior.

## Objections
| Objection | Response |
|-----------|----------|
| "Isn't this just tracing/logging?" | AgentDbg is optimized as a debugger workflow: timeline-first, local-first, and focused on root-cause clarity per run. |
| "I don't want framework lock-in." | Core instrumentation is framework-agnostic; integrations are optional adapters. |
| "Will this leak sensitive data?" | Redaction is enabled by default and data remains local on your machine. |
| "Will this slow things down?" | The stack is intentionally minimal and local; no network dependency in core flow. |

**Anti-persona:**  
Teams primarily seeking enterprise observability (dashboards/alerts/compliance/RBAC) as the immediate outcome.

## Switching Dynamics
**Push:**  
Unclear failures, costly loops, and brittle debugging in existing workflows.

**Pull:**  
Immediate local timeline clarity plus guardrails that prevent budget-burning runs.

**Habit:**  
Teams are used to print/log debugging and existing vendor dashboards.

**Anxiety:**  
Concern about integration effort, data handling, and whether it helps with real edge cases.

## Customer Language
**How they describe the problem:**
- "Why did it call that tool?"
- "It worked yesterday."
- "My agent keeps looping."
- "I don't really know what my agent is doing."

**How they describe us:**
- "A debugger for AI agents."
- "Step-through debugging for agent runs."
- "Local-first timeline of what actually happened."

**Words to use:**  
debugger, timeline, run, loop warning, guardrails, local-first, evidence, fix fast

**Words to avoid:**  
observability, monitoring, dashboards, alerts, enterprise platform, spend analytics

**Glossary:**
| Term | Meaning |
|------|---------|
| Run | One top-level agent execution |
| Event | A structured step in the run timeline |
| Loop warning | Repeating pattern detected in recent events |
| Guardrail | Configured stop condition for runaway behavior |
| Local-first | Data stays on the developer's machine |

## Brand Voice
**Tone:**  
Technical, direct, confident, practical.

**Style:**  
Concrete and example-led; short sentences; minimal buzzwords.

**Personality:**  
Clear, pragmatic, trustworthy, engineer-first.

## Proof Points
**Metrics:**
- 187 tests across 17 files (from internal project docs)
- ~75% coverage (from internal project docs)

**Customers:**  
Early-stage adoption (public logos not yet established).

**Testimonials:**  
No formal testimonials yet; use internal/early-user problem statements until validated quotes are collected.

**Value themes:**
| Theme | Proof |
|-------|-------|
| Fast insight | "<10 minutes to first useful timeline" product promise |
| Cost protection | Guardrails stop loops and threshold breaches mid-run |
| Trust and control | Local storage + redaction defaults + no cloud requirement |

## Goals
**Business goal:**  
Become the default local debugger workflow for Python agent builders.

**Conversion action:**  
Install and run first trace (`pip install agentdbg` -> run agent -> `agentdbg view`).

**Current metrics:**  
Early-stage OSS traction; success measured by concrete debugging wins and repeated usage.

