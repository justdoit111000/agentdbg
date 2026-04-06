# AgentDbg Website Design Brief (Minimalist Dark)

*Last updated: 2026-04-05*  
*Source style system: `/Users/aaa/agentdbg-main/design-instructions.md`*

## 1) Design Intent
Create a premium, calm, developer-focused site that feels like a late-night debugging environment:
- atmospheric dark layers (not pure black)
- warm amber accent
- glass cards + subtle ambient glow
- high readability and generous spacing

## 2) Visual Direction Rules
### Non-negotiables
1. Layered slate backgrounds: `#0A0A0F -> #12121A -> #1A1A24`
2. Warm amber accent: `#F59E0B`
3. Ambient glow used sparingly for emphasis
4. Glass cards (`rgba(26,26,36,0.6)` + blur)
5. Spacious sections (`py-24 md:py-32 lg:py-40`)
6. Subtle borders (`rgba(255,255,255,0.08)`)

### Never do
- bright neon palette
- pure black flat surfaces everywhere
- busy gradient-heavy hero clutter
- long dense paragraphs with weak hierarchy

## 3) Typography System
### Font roles
- Headline/display: `Space Grotesk`
- Body/interface: `Inter`
- Code snippets/CLI: `JetBrains Mono`

### Hierarchy targets
- Hero headline: `text-5xl md:text-6xl lg:text-7xl`
- Section title: `text-3xl md:text-4xl`
- Body: `text-base md:text-lg`
- Meta/support copy: `text-sm`

## 4) Page-Level Layout
### Homepage section rhythm
1. Hero
2. Trust strip (local-first statement)
3. Problem
4. Solution/timeline features
5. Guardrails
6. Integrations
7. Quickstart steps
8. FAQ
9. Final CTA

### Layout rules
- Max width: `max-w-6xl`
- Horizontal padding: `px-6 md:px-8 lg:px-12`
- Card radius: `rounded-lg` default
- Button radius: `rounded-lg`

## 5) Component Styling Notes
### Buttons
- Primary button is amber with dark text.
- Hover: increase brightness + amber glow.
- Active: subtle press (`scale-[0.98]`).
- Focus-visible ring always amber.

### Cards
- Semi-transparent dark surface with blur.
- Border opacity rises on hover.
- Interactive cards use subtle scale (`1.02`) and shadow increase.

### Inputs (if email capture is added later)
- Dark glass background.
- Soft border + amber focus ring.
- Minimum `h-11` for touch.

## 6) Motion & Interaction
- Transition timing: 200ms (buttons/links), 300ms (cards)
- Avoid springy/bouncy animations
- Use gentle reveal and hover states
- FAQ expansion should animate height + opacity smoothly

## 7) Accessibility Checklist
- Keep body text contrast >= WCAG AA on dark background
- Ensure focus-visible styles on all interactive elements
- Maintain 44px minimum touch targets
- Preserve readability at mobile sizes (no tiny low-contrast text)

## 8) Asset & Imagery Direction
- Prefer product-in-context visuals (terminal/code/editor + timeline UI)
- Avoid generic handshake/startup stock photos
- Use screenshots/GIF snippets from real AgentDbg flows where possible
- Keep decorative ambient orbs low-opacity so content remains dominant

## 9) Implementation Notes (for build phase)
- Centralize tokens via CSS variables first.
- Build reusable primitives (`Section`, `Card`, `CTAButton`, `CodeBlock`).
- Keep one visual language across homepage and subpages.
- Reuse the same CTA style and wording hierarchy everywhere.

