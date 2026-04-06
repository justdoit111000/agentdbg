#!/usr/bin/env python3
"""Generate static blog pages from markdown files in this directory."""

from __future__ import annotations

import html
import json
import math
import re
import subprocess
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


BLOG_DIR = Path(__file__).resolve().parent
SITE_DIR = BLOG_DIR.parent
BASE_URL = "https://agentdbg.com"
OG_IMAGE_URL = f"{BASE_URL}/assets/timeline-pure-python.gif"
LOGO_IMAGE_URL = f"{BASE_URL}/assets/AgentDbg%20logo%20white.png"
WORDS_PER_MINUTE = 220

POST_METADATA = {
    "01-quick-start-guide-debug-your-first-ai-agent-in-10-minutes.md": {
        "category": "Quick Start",
        "tags": ["quick-start", "python", "agent-debugging"],
        "published": "2025-01-14",
        "description": "Ship your first traced AI agent in 10 minutes with a practical AgentDbg setup, timeline walkthrough, and guardrail defaults.",
    },
    "02-common-agent-debugging-pitfalls-and-solutions.md": {
        "category": "Troubleshooting",
        "tags": ["pitfalls", "debugging", "guardrails"],
        "published": "2025-01-29",
        "description": "Diagnose the 7 most common agent-debugging failures and apply repeatable fixes using structured traces, loop detection, and clear error context.",
    },
    "03-building-customer-support-agent-with-agentdbg.md": {
        "category": "Tutorial",
        "tags": ["customer-support", "langchain", "production"],
        "published": "2025-02-10",
        "description": "Build a production-minded customer support agent with LangChain, AgentDbg guardrails, escalation flows, and cost-aware debugging patterns.",
    },
    "04-complete-langchain-agent-debugging-workflow.md": {
        "category": "Advanced",
        "tags": ["langchain", "workflow", "production"],
        "published": "2025-02-26",
        "description": "Implement a full LangChain debugging workflow from local development to production incident response with actionable AgentDbg instrumentation.",
    },
}

IGNORED_MARKDOWN_FILES = {"README.md"}

CATEGORY_RULES: tuple[tuple[str, str], ...] = (
    ("quick-start", "Quick Start"),
    ("pitfall", "Troubleshooting"),
    ("troubleshoot", "Troubleshooting"),
    ("workflow", "Advanced"),
    ("tutorial", "Tutorial"),
    ("architecture", "Architecture"),
    ("schema", "Reference"),
    ("reference", "Reference"),
    ("security", "Security"),
    ("privacy", "Security"),
    ("production", "Production"),
    ("guide", "Guide"),
)

TAG_STOPWORDS = {
    "a",
    "an",
    "and",
    "for",
    "in",
    "of",
    "the",
    "to",
    "under",
    "with",
    "how",
    "your",
    "first",
    "complete",
}


@dataclass(frozen=True)
class TocItem:
    level: int
    anchor: str
    text: str


@dataclass(frozen=True)
class Post:
    source_path: Path
    slug: str
    title: str
    description: str
    excerpt: str
    category: str
    tags: tuple[str, ...]
    reading_time_min: int
    word_count: int
    published: date
    updated: date
    body_html: str
    toc: tuple[TocItem, ...]

    @property
    def article_path(self) -> str:
        return f"{self.slug}.html"

    @property
    def absolute_url(self) -> str:
        return f"{BASE_URL}/blog/{self.slug}"


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return re.sub(r"-{2,}", "-", value).strip("-")


def strip_markdown(value: str) -> str:
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"\1", value)
    value = re.sub(r"\*([^*]+)\*", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"!\[[^\]]*]\([^)]+\)", "", value)
    return re.sub(r"\s+", " ", value).strip()


def word_count(markdown_text: str) -> int:
    # Include code/text tokens so read-time estimates match practical reading effort.
    return len(re.findall(r"[A-Za-z0-9_]+", markdown_text))


def first_content_paragraph(markdown_text: str) -> str:
    chunks = re.split(r"\n\s*\n", markdown_text)
    for chunk in chunks:
        line = chunk.strip()
        if not line:
            continue
        if line.startswith("#") or line.startswith("```"):
            continue
        if line.startswith("- ") or re.match(r"^\d+\.\s", line):
            continue
        paragraph = strip_markdown(line)
        if paragraph:
            return paragraph
    return "Practical guide for building and debugging AI agents with AgentDbg."


def normalize_intro_text(value: str) -> str:
    return re.sub(r"^(Experience|Expertise|Authoritativeness|Trustworthiness):\s*", "", value, flags=re.I)


def clip_at_word_boundary(value: str, max_len: int) -> str:
    if len(value) <= max_len:
        return value
    clipped = value[: max_len + 1]
    if " " in clipped:
        clipped = clipped.rsplit(" ", 1)[0]
    return clipped.rstrip(" ,;:-") + "..."


def first_sentence(value: str) -> str:
    match = re.search(r"^(.+?[.!?])(\s|$)", value)
    if match:
        return match.group(1).strip()
    return value.strip()


def render_markdown_to_html(path: Path) -> str:
    result = subprocess.run(
        ["pandoc", "--from=gfm", "--to=html5", str(path)],
        capture_output=True,
        text=True,
        check=True,
    )
    html_output = result.stdout.strip()
    # We render the page title separately in the article hero.
    html_output = re.sub(r"<h1[^>]*>.*?</h1>\s*", "", html_output, count=1, flags=re.S)
    return html_output


def extract_toc(body_html: str) -> tuple[TocItem, ...]:
    toc_items: list[TocItem] = []
    for match in re.finditer(r"<h([23]) id=\"([^\"]+)\">(.*?)</h\1>", body_html, re.S):
        level = int(match.group(1))
        anchor = match.group(2)
        raw_text = re.sub(r"<[^>]+>", "", match.group(3))
        text = html.unescape(raw_text).strip()
        if text:
            toc_items.append(TocItem(level=level, anchor=anchor, text=text))
    return tuple(toc_items)


def infer_category(slug: str, title: str) -> str:
    haystack = f"{slug} {title}".lower()
    for keyword, category in CATEGORY_RULES:
        if keyword in haystack:
            return category
    return "Guide"


def infer_tags(slug: str, title: str) -> tuple[str, ...]:
    raw_tokens = [token for token in re.split(r"[^a-z0-9]+", f"{slug.lower()} {title.lower()}") if token]
    deduped: list[str] = []
    for token in raw_tokens:
        if token in TAG_STOPWORDS or len(token) <= 2:
            continue
        if token not in deduped:
            deduped.append(token)

    tags: list[str] = []
    if "agent" in deduped and "debugging" in deduped:
        tags.append("agent-debugging")

    for token in deduped:
        if token == "agentdbg":
            tags.append("agentdbg")
            continue
        if token in {"langchain", "openai", "production", "security", "privacy", "architecture", "schema", "workflow", "tutorial"}:
            tags.append(token)
            continue
        if len(tags) >= 5:
            break

    # Always keep at least 3 tags for filtering + interlinking.
    for token in deduped:
        if len(tags) >= 5:
            break
        if token not in tags:
            tags.append(token)

    return tuple(tags[:5]) if tags else ("guide",)


def infer_published(md_file: Path, metadata: dict[str, object]) -> date:
    published_value = metadata.get("published")
    if isinstance(published_value, str):
        return date.fromisoformat(published_value)
    return datetime.fromtimestamp(md_file.stat().st_mtime).date()


def article_header(current: str) -> str:
    blog_link = "index.html" if current == "blog" else "../blog/index.html"
    root_prefix = ".." if current == "blog" else "."
    logo_src = f"{root_prefix}/assets/AgentDbg logo white.png"
    docs_link = "https://github.com/AgentDbg/AgentDbg/blob/main/docs/getting-started.md"
    github_link = "https://github.com/AgentDbg/AgentDbg"
    return f"""
    <header class="site-header">
      <div class="container header-inner">
        <a class="brand" href="{root_prefix}/index.html"><img class="brand-logo" src="{logo_src}" alt="AgentDbg logo" /></a>
        <button class="menu-toggle" type="button" aria-label="Toggle navigation" aria-expanded="false" data-menu-toggle>
          Menu
        </button>
        <nav class="nav-links" data-nav-links>
          <a href="{root_prefix}/index.html#product">Product</a>
          <a href="{root_prefix}/guardrails.html">Guardrails</a>
          <a href="{root_prefix}/integrations/index.html">Integrations</a>
          <a href="{blog_link}" aria-current="page">Blog</a>
          <a href="{docs_link}">Docs</a>
          <a href="{github_link}">GitHub</a>
          <a class="btn btn-primary" href="{root_prefix}/index.html#quickstart">Install AgentDbg</a>
        </nav>
      </div>
    </header>
    """


def site_footer(current: str) -> str:
    root_prefix = ".." if current == "blog" else "."
    blog_link = "index.html" if current == "blog" else "../blog/index.html"
    logo_src = f"{root_prefix}/assets/AgentDbg logo white.png"
    return f"""
    <footer class="site-footer">
      <div class="container footer-grid">
        <div>
          <a class="brand" href="{root_prefix}/index.html"><img class="brand-logo" src="{logo_src}" alt="AgentDbg logo" /></a>
          <p class="spacer-top">Local-first debugger for AI agents.</p>
          <p class="footer-email"><a href="mailto:hello@agentdbg.com">hello@agentdbg.com</a></p>
        </div>
        <div>
          <h3>Product</h3>
          <div class="footer-links">
            <a href="{root_prefix}/index.html#product">Overview</a>
            <a href="{root_prefix}/guardrails.html">Guardrails</a>
            <a href="{root_prefix}/integrations/index.html">Integrations</a>
            <a href="{blog_link}">Blog</a>
          </div>
        </div>
        <div>
          <h3>Docs</h3>
          <div class="footer-links">
            <a href="https://github.com/AgentDbg/AgentDbg/blob/main/docs/getting-started.md">Getting Started</a>
            <a href="https://github.com/AgentDbg/AgentDbg/blob/main/docs/integrations.md">Integrations</a>
            <a href="https://github.com/AgentDbg/AgentDbg/blob/main/docs/architecture.md">Architecture</a>
          </div>
        </div>
        <div>
          <h3>Community</h3>
          <div class="footer-links">
            <a href="https://github.com/AgentDbg/AgentDbg">GitHub</a>
            <a href="https://pypi.org/project/agentdbg/">PyPI</a>
            <a href="{blog_link}#topics">Topics</a>
          </div>
        </div>
      </div>
    </footer>
    """


def fmt_human_date(value: date) -> str:
    return value.strftime("%b %d, %Y")


def render_toc(items: tuple[TocItem, ...]) -> str:
    if not items:
        return "<p class=\"blog-muted\">This article has no section headings yet.</p>"
    links = []
    for item in items:
        indent_class = "blog-toc-subitem" if item.level == 3 else ""
        links.append(
            f"<a class=\"blog-toc-link {indent_class}\" data-toc-link href=\"#{item.anchor}\">{html.escape(item.text)}</a>"
        )
    return "".join(links)


def article_json_ld(post: Post) -> str:
    payload = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post.title,
        "description": post.description,
        "datePublished": post.published.isoformat(),
        "dateModified": post.updated.isoformat(),
        "author": {
            "@type": "Organization",
            "name": "AgentDbg Editorial Team",
            "url": f"{BASE_URL}/blog/#authors",
        },
        "publisher": {
            "@type": "Organization",
            "name": "AgentDbg",
            "url": BASE_URL,
            "logo": {
                "@type": "ImageObject",
                "url": LOGO_IMAGE_URL,
            },
        },
        "image": OG_IMAGE_URL,
        "mainEntityOfPage": post.absolute_url,
        "articleSection": list(post.tags),
        "wordCount": post.word_count,
    }
    return json.dumps(payload, ensure_ascii=True, indent=2)


def listing_json_ld(posts: list[Post]) -> str:
    payload = {
        "@context": "https://schema.org",
        "@type": "Blog",
        "name": "AgentDbg Blog",
        "url": f"{BASE_URL}/blog/",
        "blogPost": [
            {"@type": "BlogPosting", "headline": p.title, "url": p.absolute_url} for p in posts
        ],
    }
    return json.dumps(payload, ensure_ascii=True, indent=2)


def related_posts(current: Post, posts: list[Post], limit: int = 3) -> list[Post]:
    scored: list[tuple[int, Post]] = []
    current_tags = set(current.tags)
    for post in posts:
        if post.slug == current.slug:
            continue
        overlap = len(current_tags.intersection(set(post.tags)))
        same_category = 1 if post.category == current.category else 0
        score = overlap * 3 + same_category
        scored.append((score, post))
    scored.sort(key=lambda item: (item[0], item[1].published), reverse=True)
    return [post for _, post in scored[:limit]]


def inject_inline_interlinks(body_html: str, posts: list[Post]) -> str:
    cards = []
    for post in posts[:2]:
        cards.append(
            f"""
            <a class="blog-inline-related-link" href="{post.article_path}">
              <strong>{html.escape(post.title)}</strong>
              <span>{post.reading_time_min} min read</span>
            </a>
            """
        )
    block = f"""
    <aside class="blog-inline-related">
      <h3>Related reading</h3>
      <p>Follow these guides next to keep your debugging workflow connected end-to-end.</p>
      <div class="blog-inline-related-grid">
        {''.join(cards)}
      </div>
    </aside>
    """
    return body_html.replace("</p>", f"</p>{block}", 1)


def render_sitemap_xml(posts: list[Post]) -> str:
    today = date.today().isoformat()
    rows = [
        (f"{BASE_URL}/", today),
        (f"{BASE_URL}/guardrails", today),
        (f"{BASE_URL}/integrations/", today),
        (f"{BASE_URL}/integrations/openai-agents", today),
        (f"{BASE_URL}/blog/", today),
    ]
    rows.extend((post.absolute_url, post.updated.isoformat()) for post in posts)

    url_nodes = []
    for loc, lastmod in rows:
        url_nodes.append(
            "  <url>\n"
            f"    <loc>{loc}</loc>\n"
            f"    <lastmod>{lastmod}</lastmod>\n"
            "  </url>"
        )
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n"
        f"{chr(10).join(url_nodes)}\n"
        "</urlset>\n"
    )


def render_robots_txt() -> str:
    return (
        "# AgentDbg crawl policy\n"
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        "User-agent: GPTBot\n"
        "Allow: /\n"
        "\n"
        "User-agent: ChatGPT-User\n"
        "Allow: /\n"
        "\n"
        "User-agent: ClaudeBot\n"
        "Allow: /\n"
        "\n"
        "User-agent: anthropic-ai\n"
        "Allow: /\n"
        "\n"
        "User-agent: PerplexityBot\n"
        "Allow: /\n"
        "\n"
        "User-agent: Google-Extended\n"
        "Allow: /\n"
        "\n"
        f"Sitemap: {BASE_URL}/sitemap.xml\n"
    )


def render_llms_txt(posts: list[Post]) -> str:
    lines = [
        "# AgentDbg",
        "",
        "> Local-first debugger for AI agents. Trace runs, inspect LLM/tool calls, and stop runaway loops with guardrails.",
        "",
        "## Canonical URLs",
        f"- Homepage: {BASE_URL}/",
        f"- Guardrails: {BASE_URL}/guardrails",
        f"- Integrations: {BASE_URL}/integrations/",
        f"- Blog index: {BASE_URL}/blog/",
        "",
        "## Product docs",
        "- Getting started: https://github.com/AgentDbg/AgentDbg/blob/main/docs/getting-started.md",
        "- Guardrails docs: https://github.com/AgentDbg/AgentDbg/blob/main/docs/guardrails.md",
        "- Integrations docs: https://github.com/AgentDbg/AgentDbg/blob/main/docs/integrations.md",
        "",
        "## Selected blog posts",
    ]
    for post in posts[:12]:
        lines.append(f"- {post.title}: {post.absolute_url}")
    lines.extend(
        [
            "",
            "## Contact",
            "- hello@agentdbg.com",
        ]
    )
    return "\n".join(lines) + "\n"


def render_article_page(post: Post, posts: list[Post]) -> str:
    rel_posts = related_posts(post, posts)
    body_with_interlinks = inject_inline_interlinks(post.body_html, rel_posts)
    idx = posts.index(post)
    newer = posts[idx - 1] if idx > 0 else None
    older = posts[idx + 1] if idx < len(posts) - 1 else None

    related_cards = []
    for rel in rel_posts:
        related_cards.append(
            f"""
            <article class="glass card blog-mini-card">
              <p class="blog-card-kicker">{html.escape(rel.category)}</p>
              <h3><a href="{rel.article_path}">{html.escape(rel.title)}</a></h3>
              <p>{html.escape(rel.excerpt)}</p>
              <div class="blog-card-footer">
                <span>{fmt_human_date(rel.published)}</span>
                <span>{rel.reading_time_min} min read</span>
              </div>
            </article>
            """
        )

    prev_next = []
    if newer:
        prev_next.append(
            f'<a class="blog-prevnext-link" href="{newer.article_path}"><span>Newer</span><strong>{html.escape(newer.title)}</strong></a>'
        )
    if older:
        prev_next.append(
            f'<a class="blog-prevnext-link" href="{older.article_path}"><span>Older</span><strong>{html.escape(older.title)}</strong></a>'
        )
    prev_next_html = "".join(prev_next) or "<p class=\"blog-muted\">No adjacent article found.</p>"

    html_content = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{html.escape(post.title)} | AgentDbg Blog</title>
    <meta name="description" content="{html.escape(post.description)}" />
    <meta name="author" content="AgentDbg Editorial Team" />
    <meta name="robots" content="index,follow,max-image-preview:large" />
    <meta property="og:site_name" content="AgentDbg" />
    <meta property="og:title" content="{html.escape(post.title)}" />
    <meta property="og:description" content="{html.escape(post.description)}" />
    <meta property="og:type" content="article" />
    <meta property="og:url" content="{post.absolute_url}" />
    <meta property="og:image" content="{OG_IMAGE_URL}" />
    <meta property="og:image:alt" content="AgentDbg timeline view and guardrail debugging workflow" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{html.escape(post.title)} | AgentDbg Blog" />
    <meta name="twitter:description" content="{html.escape(post.description)}" />
    <meta name="twitter:image" content="{OG_IMAGE_URL}" />
    <link rel="canonical" href="{post.absolute_url}" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&family=Space+Grotesk:wght@500;600;700&display=swap"
      rel="stylesheet"
    />
    <link rel="stylesheet" href="../assets/styles.css" />
    <script type="application/ld+json">
{article_json_ld(post)}
    </script>
  </head>
  <body>
    <div class="ambient-orb orb-top"></div>
    <div class="ambient-orb orb-bottom"></div>
    {article_header(current="blog")}
    <main>
      <section class="section-compact">
        <div class="container blog-breadcrumbs">
          <a href="../index.html">Home</a>
          <span>/</span>
          <a href="index.html">Blog</a>
          <span>/</span>
          <span>{html.escape(post.title)}</span>
        </div>
        <div class="container blog-article-hero">
          <span class="eyebrow"><span class="pulse"></span>AgentDbg Engineering Blog</span>
          <h1 class="spacer-top">{html.escape(post.title)}</h1>
          <p class="lede">{html.escape(post.description)}</p>
          <div class="blog-meta-row">
            <span><strong>Author:</strong> <a href="index.html#authors">AgentDbg Editorial Team</a></span>
            <span><strong>Published:</strong> <time datetime="{post.published.isoformat()}">{fmt_human_date(post.published)}</time></span>
            <span><strong>Updated:</strong> <time datetime="{post.updated.isoformat()}">{fmt_human_date(post.updated)}</time></span>
            <span><strong>Read time:</strong> {post.reading_time_min} min</span>
          </div>
          <div class="pill-row">
            {''.join(f'<span class="pill">{html.escape(tag)}</span>' for tag in post.tags)}
          </div>
          <div class="cta-group">
            <button class="btn btn-outline" type="button" data-copy-value="{post.absolute_url}">Copy article link</button>
            <a class="btn btn-outline" href="index.html">Back to all posts</a>
          </div>
        </div>
      </section>

      <section class="section-compact">
        <div class="container blog-article-layout">
          <aside class="glass blog-toc">
            <h3>Table of contents</h3>
            <nav class="blog-toc-nav">
              {render_toc(post.toc)}
            </nav>
          </aside>
          <article class="glass blog-article-content">
            {body_with_interlinks}
          </article>
        </div>
      </section>

      <section class="section-compact">
        <div class="container">
          <div class="blog-related-head">
            <h2>Continue reading</h2>
            <p>Interlinked tutorials to keep context between setup, troubleshooting, and production workflows.</p>
          </div>
          <div class="grid grid-3 blog-mini-grid">
            {''.join(related_cards)}
          </div>
        </div>
      </section>

      <section class="section-compact">
        <div class="container blog-prevnext">
          {prev_next_html}
        </div>
      </section>

      <section class="section-compact">
        <div class="container glass card section-highlight blog-cta">
          <h2>Ready to debug your next agent run?</h2>
          <p class="lede">Install AgentDbg, trace one run, and use this blog as your playbook for faster incident resolution.</p>
          <div class="cta-group">
            <a class="btn btn-primary" href="../index.html#quickstart">Install AgentDbg</a>
            <a class="btn btn-outline" href="../integrations/index.html">Explore integrations</a>
          </div>
        </div>
      </section>
    </main>
    {site_footer(current="blog")}
    <script src="../assets/app.js"></script>
  </body>
</html>
"""
    return html_content


def render_index_page(posts: list[Post]) -> str:
    all_tags = sorted({tag for post in posts for tag in post.tags})
    cards = []
    for idx, post in enumerate(posts):
        featured_class = "section-highlight" if idx == 0 else ""
        card_tags = ",".join(post.tags)
        cards.append(
            f"""
            <article class="glass card blog-list-card {featured_class}" data-blog-card data-tags="{html.escape(card_tags)}" data-title="{html.escape(post.title.lower())}" data-excerpt="{html.escape(post.excerpt.lower())}">
              <div class="blog-card-meta">
                <span>{html.escape(post.category)}</span>
                <span>{fmt_human_date(post.published)}</span>
              </div>
              <h3><a href="{post.article_path}">{html.escape(post.title)}</a></h3>
              <p>{html.escape(post.excerpt)}</p>
              <div class="pill-row">
                {''.join(f'<span class="pill">{html.escape(tag)}</span>' for tag in post.tags)}
              </div>
              <div class="blog-card-footer">
                <span>{post.reading_time_min} min read</span>
                <a class="blog-read-link" href="{post.article_path}">Read article</a>
              </div>
            </article>
            """
        )

    filter_chips = ['<button class="pill blog-filter-pill is-active" type="button" data-blog-tag="all">All topics</button>']
    for tag in all_tags:
        filter_chips.append(
            f'<button class="pill blog-filter-pill" type="button" data-blog-tag="{html.escape(tag)}">{html.escape(tag)}</button>'
        )

    html_content = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AgentDbg Blog | Guides for AI Agent Debugging</title>
    <meta
      name="description"
      content="Practical tutorials, debugging workflows, and production playbooks for building and maintaining AI agents with AgentDbg."
    />
    <meta name="robots" content="index,follow,max-image-preview:large" />
    <meta property="og:site_name" content="AgentDbg" />
    <meta property="og:title" content="AgentDbg Blog | Guides for AI Agent Debugging" />
    <meta property="og:description" content="Explore quick starts, troubleshooting patterns, and production-ready tutorials for AI agents." />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="{BASE_URL}/blog/" />
    <meta property="og:image" content="{OG_IMAGE_URL}" />
    <meta property="og:image:alt" content="AgentDbg blog featuring AI agent debugging guides" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="AgentDbg Blog | Guides for AI Agent Debugging" />
    <meta name="twitter:description" content="Practical tutorials and production playbooks for AI agent debugging." />
    <meta name="twitter:image" content="{OG_IMAGE_URL}" />
    <link rel="canonical" href="{BASE_URL}/blog/" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&family=Space+Grotesk:wght@500;600;700&display=swap"
      rel="stylesheet"
    />
    <link rel="stylesheet" href="../assets/styles.css" />
    <script type="application/ld+json">
{listing_json_ld(posts)}
    </script>
  </head>
  <body>
    <div class="ambient-orb orb-top"></div>
    <div class="ambient-orb orb-bottom"></div>
    {article_header(current="blog")}
    <main>
      <section class="section">
        <div class="container">
          <span class="eyebrow"><span class="pulse"></span>Field guides for AI agent teams</span>
          <h1 class="spacer-top">AgentDbg Blog</h1>
          <p class="lede">
            Actionable debugging playbooks with clear author attribution, reading-time estimates, interlinked tutorials, and production-tested implementation examples.
          </p>
          <div class="blog-controls">
            <label class="blog-search-wrap">
              <span class="blog-control-label">Search articles</span>
              <input class="blog-search-input" type="search" placeholder="Search by topic, framework, or workflow..." data-blog-search />
            </label>
            <div class="blog-filter-row" id="topics">
              {''.join(filter_chips)}
            </div>
            <p class="blog-count" data-blog-count></p>
          </div>
        </div>
      </section>

      <section class="section-compact">
        <div class="container grid grid-2 blog-list-grid">
          {''.join(cards)}
        </div>
      </section>

      <section class="section-compact" id="authors">
        <div class="container glass card">
          <h2>About the authors</h2>
          <p>
            Articles are written and reviewed by the AgentDbg engineering team with production debugging experience across LangChain, OpenAI Agents SDK, and framework-agnostic Python stacks.
          </p>
          <div class="cta-group">
            <a class="btn btn-outline" href="https://github.com/AgentDbg/AgentDbg">View the open-source project</a>
            <a class="btn btn-outline" href="../integrations/index.html">See integration guides</a>
          </div>
        </div>
      </section>
    </main>
    {site_footer(current="blog")}
    <script src="../assets/app.js"></script>
  </body>
</html>
"""
    return html_content


def build_posts() -> list[Post]:
    posts: list[Post] = []
    for md_file in sorted(BLOG_DIR.glob("*.md")):
        if md_file.name in IGNORED_MARKDOWN_FILES:
            continue

        metadata = POST_METADATA.get(md_file.name, {})
        markdown_text = md_file.read_text(encoding="utf-8")

        title_match = re.search(r"^#\s+(.+)$", markdown_text, flags=re.M)
        if not title_match:
            raise ValueError(f"Could not find title in {md_file.name}")

        title = title_match.group(1).strip()
        intro = normalize_intro_text(first_content_paragraph(markdown_text))
        description_override = metadata.get("description")
        if isinstance(description_override, str) and description_override.strip():
            description = description_override.strip()
        else:
            description = clip_at_word_boundary(first_sentence(intro), 190)
        excerpt = clip_at_word_boundary(intro, 220)
        published = infer_published(md_file, metadata)
        updated = max(
            published,
            datetime.fromtimestamp(md_file.stat().st_mtime).date(),
        )
        total_words = word_count(markdown_text)
        reading_time = max(1, math.ceil(total_words / WORDS_PER_MINUTE))
        slug = re.sub(r"^[0-9]+-", "", md_file.stem)
        slug = re.sub(r"^agentdbg-", "", slug)
        html_body = render_markdown_to_html(md_file)
        toc_items = extract_toc(html_body)

        posts.append(
            Post(
                source_path=md_file,
                slug=slugify(slug),
                title=title,
                description=description,
                excerpt=excerpt,
                category=str(metadata.get("category")) if isinstance(metadata.get("category"), str) else infer_category(slug, title),
                tags=tuple(metadata.get("tags")) if isinstance(metadata.get("tags"), list) else infer_tags(slug, title),
                reading_time_min=reading_time,
                word_count=total_words,
                published=published,
                updated=updated,
                body_html=html_body,
                toc=toc_items,
            )
        )

    posts.sort(key=lambda post: post.published, reverse=True)
    return posts


def write_output(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    posts = build_posts()
    expected_pages = {f"{post.slug}.html" for post in posts}
    expected_pages.add("index.html")
    removed_pages: list[str] = []
    for existing_page in BLOG_DIR.glob("*.html"):
        if existing_page.name not in expected_pages:
            existing_page.unlink()
            removed_pages.append(existing_page.name)

    write_output(BLOG_DIR / "index.html", render_index_page(posts))
    for post in posts:
        write_output(BLOG_DIR / f"{post.slug}.html", render_article_page(post, posts))
    write_output(SITE_DIR / "sitemap.xml", render_sitemap_xml(posts))
    write_output(SITE_DIR / "robots.txt", render_robots_txt())
    write_output(SITE_DIR / "llms.txt", render_llms_txt(posts))
    print(f"Generated blog index + {len(posts)} article pages in {BLOG_DIR}")
    if removed_pages:
        print(f"Removed stale pages: {', '.join(sorted(removed_pages))}")
    print(f"Generated crawl files in {SITE_DIR}")


if __name__ == "__main__":
    main()
