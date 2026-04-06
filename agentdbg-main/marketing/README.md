# AgentDbg Marketing Site

This directory contains a standalone static marketing site for AgentDbg.

## Pages
- `index.html` — homepage
- `guardrails.html` — guardrails deep-dive page
- `integrations/index.html` — integrations overview
- `integrations/openai-agents.html` — integration detail template page
- `blog/index.html` — blog listing with search/topic filters
- `blog/*.html` — generated blog article pages

## Local preview

From repository root:

```bash
python -m http.server 8713
```

Then open:

- `http://127.0.0.1:8713/marketing/index.html`
- `http://127.0.0.1:8713/marketing/blog/index.html`

## Notes
- Styling and interactions are shared via `assets/styles.css` and `assets/app.js`.
- Product demo media currently references `docs/assets/*` from this repository.
- Blog pages are generated from markdown sources with `python3 blog/build_blog.py`.
