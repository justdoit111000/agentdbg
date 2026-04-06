# AgentDbg SEO + GEO Audit Report

Date: April 6, 2026
Scope: `https://agentdbg.com/` live site + `marketing/` website codebase
Methods used: technical SEO audit, GEO/AI-citation readiness checks, structured metadata scan, crawl-file validation, rendered-page checks

## Executive Summary

The site had strong core content but critical crawl/discovery and canonicalization issues that blocked SEO/GEO effectiveness:

1. `robots.txt`, `sitemap.xml`, and `llms.txt` were not properly served on production (homepage HTML was returned).
2. AI crawlers (`GPTBot`, `ClaudeBot`) were explicitly disallowed in production policy.
3. Core marketing pages lacked canonical + Open Graph + Twitter + JSON-LD metadata.
4. Blog canonicals and OG URLs referenced `agentdbg.dev` instead of `agentdbg.com`.
5. Blog pipeline produced duplicate URL variants for some posts.
6. Multiple internal content links pointed to dead subdomains (`docs.agentdbg.com`, `forum.agentdbg.com`).

All issues above were fixed at source level in the codebase.

## Baseline Findings (Before Fix)

### Critical

- Crawl endpoints invalid on live domain
  - `https://agentdbg.com/robots.txt` returned Cloudflare-managed block content plus homepage HTML.
  - `https://agentdbg.com/sitemap.xml` returned homepage HTML (not XML).
  - `https://agentdbg.com/llms.txt` returned homepage HTML.
- AI crawler access blocked
  - `robots.txt` disallowed `ClaudeBot`, `GPTBot`, and `Google-Extended`.
  - GEO impact: lower eligibility for AI answer-engine citation.

### High

- Missing metadata on high-value pages (`/`, `/guardrails`, `/integrations/`, `/integrations/openai-agents`)
  - Missing canonical URL, OG tags, Twitter tags, and structured JSON-LD.
- Blog canonical domain mismatch
  - Blog pages used `https://agentdbg.dev/...` for canonical + OG URL.

### Medium

- Duplicate blog URL variants from slug drift (`agentdbg-...` and non-prefixed variants), splitting authority.
- Dead links in blog content to unavailable `docs.*` and `forum.*` hosts.

## Fixes Applied

### 1) Blog pipeline canonical + GEO fixes

File: `marketing/blog/build_blog.py`

- Updated canonical base domain: `agentdbg.dev` -> `agentdbg.com`.
- Switched canonical article URLs to clean paths (no `.html` suffix in canonical).
- Added full social metadata generation to all generated blog pages:
  - `og:site_name`, `og:image`, `og:image:alt`, `twitter:title`, `twitter:description`, `twitter:image`.
- Enriched blog JSON-LD with publisher and image fields.
- Updated blog index canonical/OG URL to `https://agentdbg.com/blog/`.
- Added generated crawl artifacts:
  - `marketing/sitemap.xml`
  - `marketing/robots.txt`
  - `marketing/llms.txt`
- Fixed slug normalization to avoid duplicate article URL variants.
- Added stale-page cleanup in generator to prevent legacy duplicate pages from persisting.

### 2) Core marketing page metadata + schema

Files:
- `marketing/index.html`
- `marketing/guardrails.html`
- `marketing/integrations/index.html`
- `marketing/integrations/openai-agents.html`

Added on each page:
- Canonical URL
- Open Graph metadata
- Twitter metadata
- `robots` meta directive
- JSON-LD structured data appropriate to page type
  - Homepage: `SoftwareApplication` + `FAQPage`
  - Guardrails: `WebPage`
  - Integrations index: `CollectionPage`
  - OpenAI integration page: `TechArticle`

### 3) Dead-link mitigation

Files:
- `marketing/blog/*.md` (bulk normalization)
- `marketing/_redirects` (new)

Changes:
- Normalized legacy domains to canonical site domain where appropriate.
- Added redirects for common dead/internal destinations:
  - `/docs/*`, `/forum/*`, `/security/*`
  - CTA utility endpoints (`/assessment`, `/services`, `/training`, etc.)
  - community/newsletter placeholders

### 4) Legacy duplicate page cleanup

Deleted:
- `marketing/blog/agentdbg-architecture-deep-dive.html`
- `marketing/blog/agentdbg-production-guide.html`

(Generator now prevents these stale duplicate files from reappearing.)

## Validation Results (After Fix in Codebase)

### Metadata coverage audit across all HTML pages

- Total pages scanned: 23
- Missing `<title>`: 0
- Missing meta description: 0
- Missing canonical: 0
- Missing `og:title`: 0
- Missing `og:description`: 0
- Missing `og:url`: 0
- Missing `twitter:card`: 0
- Missing JSON-LD script: 0

### Crawl file generation

Generated and verified locally:
- `marketing/robots.txt`
- `marketing/sitemap.xml`
- `marketing/llms.txt`

### URL/canonical consistency

- Blog canonical and OG URLs now point to `https://agentdbg.com/...`.
- Duplicate slug variants were removed and canonical slug behavior is stabilized.

## GEO-Specific Improvements

- AI bot crawling policy explicitly allowed in generated `robots.txt` for:
  - `GPTBot`, `ChatGPT-User`, `ClaudeBot`, `anthropic-ai`, `PerplexityBot`, `Google-Extended`
- Added `llms.txt` with canonical URLs and high-value source pages.
- Added structured data coverage site-wide to increase machine-readability and citation eligibility.
- Improved answer-engine digestibility through normalized canonical paths and reduced duplicate pages.

## Remaining Operational Step

These code changes are complete, but production (`agentdbg.com`) will only reflect them after deploy.

Deployment workflow already exists in:
- `.github/workflows/deploy-marketing-cloudflare-pages.yml`

Once deployed, re-check:
- `https://agentdbg.com/robots.txt`
- `https://agentdbg.com/sitemap.xml`
- `https://agentdbg.com/llms.txt`
- a sample of canonical + OG tags on homepage, integrations, and blog pages
