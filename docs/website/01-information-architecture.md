# AgentDbg Website Information Architecture

*Last updated: 2026-04-05*

## 1) Site Type
Hybrid developer-product marketing site:
- product landing pages
- technical documentation entry points
- integration-focused discovery pages

## 2) Primary User Flows
### Flow A: New visitor -> First run
Homepage -> Quickstart snippet -> Docs Getting Started -> Install

### Flow B: Framework-specific visitor
Homepage / Integrations -> Integration page -> Docs Integration guide -> Install with extras

### Flow C: Skeptical evaluator
Homepage -> Guardrails section -> Architecture/Privacy trust section -> Example/demo -> Install

## 3) Navigation Model
### Header navigation (desktop)
- Product
- Guardrails
- Integrations
- Docs
- GitHub
- CTA button: `Install AgentDbg`

### Footer groups
- Product: Overview, Guardrails, Integrations, Changelog
- Docs: Getting Started, SDK, CLI, Viewer, Architecture
- Community: GitHub, Issues
- Legal: License, Security, Contributing

## 4) Sitemap (v1)
```text
Homepage (/)
├── Product (/product)
│   ├── Timeline Debugging (/product/timeline-debugging)
│   ├── Loop Detection (/product/loop-detection)
│   └── Guardrails (/product/guardrails)
├── Integrations (/integrations)
│   ├── LangChain & LangGraph (/integrations/langchain)
│   ├── OpenAI Agents SDK (/integrations/openai-agents)
│   └── CrewAI (/integrations/crewai)
├── Docs entry (/docs)
│   ├── Getting Started (/docs/getting-started)
│   ├── SDK (/docs/sdk)
│   ├── CLI (/docs/cli)
│   ├── Viewer (/docs/viewer)
│   └── Architecture (/docs/architecture)
├── Changelog (/changelog)
└── GitHub (external)
```

## 5) URL Structure Rules
- Keep URLs lowercase and human-readable.
- Use sectioned paths for product and integrations.
- Keep docs URLs aligned to existing docs structure.
- Preserve short, predictable slugs.

### URL patterns
- Product pages: `/product/{topic}`
- Integration pages: `/integrations/{framework}`
- Docs pages: `/docs/{doc-page}`

## 6) Homepage Section Structure
1. Hero (value proposition + install CTA)
2. Social proof / trust statement (local-first + no telemetry)
3. Problem section (current debugging pain)
4. Product walkthrough (timeline evidence)
5. Guardrails section (active prevention wedge)
6. Integrations strip
7. 3-step quickstart
8. FAQ / objection handling
9. Final CTA

## 7) Internal Linking Strategy
### Required links per page
- Every product page links to:
  - getting started docs
  - at least one integration page
  - install CTA
- Every integration page links to:
  - docs/integrations
  - quickstart install command
  - core product overview
- Homepage links to:
  - all three integration pages
  - docs getting-started
  - guardrails docs

### Anchor text guidance
Use descriptive anchors:
- "Stop runaway loops with guardrails"
- "Debug OpenAI Agents SDK runs"
- "See the full CLI reference"

Avoid:
- "click here"
- "learn more" as standalone anchors

## 8) IA Scope for Initial Build
Must-have pages for implementation round 1:
1. Homepage
2. Guardrails page
3. Integrations index page
4. Single integration template page

Can be phase 2:
- comparison/alternative pages
- blog/resources hub
- dedicated pricing/plan page

