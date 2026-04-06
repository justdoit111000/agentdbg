# AgentDbg Marketing Site

This directory contains a standalone static marketing site for AgentDbg.

## Pages
- `index.html` — homepage
- `guardrails.html` — guardrails deep-dive page
- `integrations/index.html` — integrations overview
- `integrations/openai-agents.html` — integration detail template page

## Local preview

From repository root:

```bash
python -m http.server 8713
```

Then open:

- `http://127.0.0.1:8713/marketing/index.html`

## Notes
- Styling and interactions are shared via `assets/styles.css` and `assets/app.js`.
- Product demo media currently references `docs/assets/*` from this repository.

