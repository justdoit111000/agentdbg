# HVAC Widget — MVP Plan (simplified)

## 0) Summary
Embed chat-style widget for HVAC websites. Modes: **Repair Estimate**, **Install Estimate**, **AI Technician** (buttons + one server prompt). Inline **Calendly** to schedule. Admin shows a simple funnel and leads. **Only US**. **English only**.

**Primary KPI:** Schedule Rate (sessions → Calendly booked). Secondary: Start→Estimate completion.

---

## 1) MVP Scope
**Must-have**
- Widget embed (launcher with company logo → chat panel with buttons).
- Repair Estimate: ≤4 questions → diagnosis+estimate from company price list → Schedule (Calendly inline).
- Install Estimate: address (Google Places US) → server ATTOM lookup → 3 packages (Good/Better/Best) → Schedule.
- Leads: first name, last name, email, phone, address (1 line) + ZIP (required before opening Calendly).
- Branding: launcher logo, chat logo, primary color, company name.
- Admin: funnel (Start → Estimate → Calendly Open → Scheduled), leads table, company settings (branding, calendly_url).

**Out of scope (v1.1+)**
- Calendly webhooks (we’ll count Scheduled via inline events first), multi-operator chat, deep analytics, JWT hardening.

---

## 2) Tech / Hosting
- **admin/**: Next.js (App Router) on Vercel; Supabase (Auth, Postgres, Storage).
- **widget/**: Vanilla TS Web Component; build with esbuild/rolldown; host on Cloudflare Pages/CDN.
- Google Places (client, restricted to US + referrers). ATTOM (server only).

---

## 2.5) Day 0 — Setup & Guardrails
**IDE_RULES.md (10 lines)**
```
- Work only within current PLAN section
- Before code: list 3–5 steps; after: summarize diff
- Don’t touch unrelated files; propose separate PR
- Keep files small (<200 lines), pure functions first
- Write/adjust E2E first; make it fail → make it pass
- After 2 bad attempts: hard reset to last green
- Read ./docs/vendor/* before coding against APIs
- Never remove logging/error handling
- Clear commits; one feature per branch
- If stuck: list hypotheses before writing code
```

**Stuck protocol** (from video): After 2 failed attempts → (a) reset to last green, (b) ask LLM for 3–4 hypotheses **without code**, (c) add minimal logs/asserts, (d) apply **one** clean fix, (e) run tests.

**Green tags**: before big AI edits → `git tag green-<YYYYMMDD-HHMM>` → revert fast if needed.

**docs/vendor/** (local docs for the agent)
- `google-places-autocomplete.md` (US-only, session tokens, Address Form mapping)
- `attom-property-lookup.md` (chosen endpoint + sample request/response)
- `calendly-inline-embed.md` (Advanced Embed, prefill, inline events)

**Seed demo**: `scripts/seed-demo.ts` creates 1 company, branding, 6 repair items, 3 install bundles.

**E2E policy**: Red→Green first. Minimal Playwright: Repair happy path; Install with ATTOM OK and ATTOM empty→manual sqft. 

**Refactor slots**: after every 2 finished sections → 30 min focused refactor under E2E safety.

---

## 3) Embed Spec
```html
<script async src="https://cdn.example.com/hvac-widget.js" data-tenant="acme"></script>
```
- Widget fetches `/api/v1/widget/bootstrap` → gets company/branding/features/calendly_url + `session_id`.
- All subsequent calls add `session_id` in body.

---

## 4) API v1 (REST)
Base: `/api/v1`

### 4.1 POST /widget/bootstrap
Request:
```json
{ "tenant": "acme", "origin": "https://www.acme-hvac.com", "utm": {"source":"web"} }
```
Response:
```json
{
  "company": {"id":"cmp_123","name":"ACME HVAC"},
  "branding": {"company_display_name":"ACME HVAC","logo_launcher_url":"...","logo_chat_url":"...","colors":{"primary":"#0F766E"}},
  "features": {"repair":true,"install":true,"ai":true},
  "calendly": {"url":"https://calendly.com/acme/repair"},
  "session": {"id":"ses_abc","expires_in_sec":1800}
}
```

### 4.2 POST /events
Request (minimal):
```json
{ "session_id":"ses_abc", "seq": 1, "name":"widget_opened", "ts": 1737300000000, "props": {"mode":"repair"} }
```
Response: `{ "ok": true }`

### 4.3 POST /repair/estimate
Request:
```json
{ "session_id":"ses_abc", "answers": [{"q":"no_cooling","a":"yes"},{"q":"thermostat","a":"blank"}] }
```
Response:
```json
{ "estimate": {"id":"est_9xy","line_items":[{"code":"TRIP","name":"Trip/Diagnostic","qty":1,"unit_price":79},{"code":"TXV_REPLACE","name":"TXV Replacement","qty":1,"unit_price":420}], "total":499, "disclaimer":"This is an estimate, not a final quote."} }
```

### 4.4 POST /install/property-lookup
Request:
```json
{
  "session_id":"ses_abc",
  "address": {
    "place_id":"ChIJ...",
    "line1":"1600 Amphitheatre Pkwy",
    "city":"Mountain View", "state":"CA", "postal_code":"94043", "country":"US",
    "lat":37.422, "lng":-122.084
  }
}
```
Response:
```json
{ "property": { "attom_id":"A123", "address_verified":true, "living_area_sqft":1850, "year_built":1998, "stories":2, "property_type":"Single Family" } }
```

### 4.5 POST /install/recommend
Request:
```json
{ "session_id":"ses_abc", "preferences": {"budget":"balanced"} }
```
Response (example):
```json
{ "packages": [
  {"tier":"Good","tonnage":3,"system_type":"AC+Gas Furnace","equipment":[{"type":"AC","model":"AC14"},{"type":"Furnace","model":"G80"}],"labor":1200,"total":6890},
  {"tier":"Better", "...":"..."},
  {"tier":"Best",   "...":"..."}
] }
```

### 4.6 POST /lead
Request:
```json
{ "session_id":"ses_abc", "contact": {"first_name":"John","last_name":"Doe","email":"john@example.com","phone":"+1 650 555 0000","address_line":"1600 Amphitheatre Pkwy, Mountain View, CA","zip":"94043"} }
```
Response: `{ "ok": true }`

### 4.7 (v1.1) POST /calendly/webhook
- Add after first installs.

---

## 5) Data Models (minimal)
```ts
// Company / Config
Company { id, name, calendly_url }
WidgetConfig { company_id, branding{ launcher_logo, chat_logo, primary_color, company_name }, features{ repair, install, ai } }

// Sessions & Events
Session { id, company_id, started_at, utm, referrer }
Event { session_id, ts, name, props }

// Repair
PricelistRepair { company_id, items[{ code, name, price }] }
Estimate { id, session_id, type: 'repair'|'install', line_items[{ code, name, qty, unit_price }], total, disclaimer? }

// Install
PropertySnapshot { session_id, attom_id?, address_line, city, state, postal_code, living_area_sqft?, year_built?, stories?, property_type? }
InstallBundles { company_id, bundles[{ tier:'Good'|'Better'|'Best', tonnage, seer2?, equipment[], labor, total_rules }] }

// Leads
Lead { id, session_id, company_id, first_name, last_name, email, phone, address_line, zip, status? }
```

---

## 6) Flows & Acceptance Criteria
### 6.1 Repair Estimate
- User opens widget → selects **Get Repair Estimate**.
- Up to 4 button steps → **Estimate** with line items + total + disclaimer.
- **Schedule** opens inline Calendly; user sees times, picks slot, enters name/email (prefilled), phone, address (prefilled from widget) → booking.
- **Analytics:** `widget_opened` → `repair.estimate_shown` → `calendly_opened` → `calendly_scheduled`.

### 6.2 Install Estimate
- Step 1: Address with Google Places **US-only**, session token; on select → server ATTOM; show property card. Fallback: manual sqft.
- Step 2: Show **3 packages** based on sqft (rule of thumb) and bundles.
- **Schedule** inline Calendly.
- **Analytics:** `install.address_selected` → `attom_lookup_ok|empty` → `install.packages_shown` → `calendly_opened` → `calendly_scheduled`.

### 6.3 AI Technician
- Buttons for common issues; short guided steps; call to action: **Schedule**.

---

## 7) Analytics (minimal)
**Events** (idempotent by `session_id` + `seq`):
- `widget_opened`
- `repair.estimate_shown` / `install.packages_shown`
- `calendly_opened`
- `calendly_scheduled` (via inline postMessage in v1)

**Event shape**
```ts
{
  session_id: string,
  seq: number,           // monotonically increasing per session
  name: string,
  ts: number,            // ms since epoch
  props?: Record<string, any>
}
```

Admin: 1 funnel chart + leads table.

---

## 8) Sprint Plan — first 4 days
**Day 1**
- Endpoints: `/widget/bootstrap`, `/events`, `/lead`.
- Admin: company settings (calendly_url, branding upload), preview widget theme.
- Widget: launcher + panel shell, load branding from bootstrap; contact form (first/last/email/phone/address/zip).

**Day 2**
- Repair: implement `/repair/estimate` (simple map rules); UI for 4-step Q&A → estimate screen.
- Calendly inline embed; capture `calendly_opened` and `calendly_scheduled` via inline events.

**Day 3**
- Install: Google Places (US), `/install/property-lookup` (server ATTOM), property card; fallback manual sqft.

**Day 4**
- Install: `/install/recommend` (sqft→tonnage→3 bundles); packages UI; polish flows; empty/error states.
- AI Technician v1: 5–7 button playbooks + one server prompt endpoint.
- Smoke E2E: Repair→Calendly happy path.

---

## 9) Risks & Defers
- Calendly inline event reliability → add webhook v1.1.
- Google/ATTOM quotas → cache address→property for 24h.
- Minimal security now; harden later (domain allow-list, JWT, webhook signatures).

---

## 10) Definition of Done (MVP)
- Widget installs with script; branding applied; EN-only (US-only address).
- Repair and Install flows operational; inline Calendly opens and we capture `calendly_scheduled` inline.
- Leads saved; funnel visible in admin; one E2E test passing.
- **Fallbacks verified**: 
  - Google Places down → free text address + ZIP accepted.
  - ATTOM empty → manual `living_area_sqft` path works.
  - Calendly blocked → open in new tab with prefill works.
- **Green tag** created before each major AI-driven change.

---

## Appendix — Skeletons
**Playwright (repair happy path, sketch)**
```ts
import { test, expect } from '@playwright/test';

test('Repair → Estimate → Calendly open', async ({ page }) => {
  await page.goto('https://demo-client-site.example');
  await page.locator('#hvac-launcher').click();
  await page.getByRole('button', { name: 'Get Repair Estimate' }).click();
  // step clicks (≤4)
  await page.getByRole('button', { name: /No cooling/i }).click();
  await page.getByRole('button', { name: /Thermostat display blank/i }).click();
  await expect(page.getByText(/Estimate/i)).toBeVisible();
  await page.getByRole('button', { name: /Schedule/i }).click();
  await expect(page.frameLocator('iframe[src*="calendly"]').locator('text=Select a Date & Time')).toBeVisible();
});
```

**Seed demo (outline)**
```ts
// scripts/seed-demo.ts
// creates: company, branding, repair items, install bundles
// run: ts-node scripts/seed-demo.ts
```

