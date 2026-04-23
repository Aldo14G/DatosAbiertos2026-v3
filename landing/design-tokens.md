# Design Tokens — DatosAbiertos NL 2026 Landing

Generated from UI/UX Pro Max skill. Civic tech / data journalism aesthetic.
References: Our World in Data, ProPublica, The Pudding, NYT Graphics.

---

## Color Palette

| Token | Hex | Usage |
|---|---|---|
| `--color-bg` | `#f9f8f5` | Page background (warm off-white, print feel) |
| `--color-surface` | `#ffffff` | Card / section backgrounds |
| `--color-surface-subtle` | `#f3f4f6` | Zebra rows, secondary surfaces |
| `--color-text` | `#0d1117` | Primary body text (near-black) |
| `--color-text-muted` | `#374151` | Secondary text (gray-700) |
| `--color-text-faint` | `#6b7280` | Captions, metadata (gray-500) |
| `--color-accent` | `#1e3a8a` | NL institutional blue (blue-900) |
| `--color-accent-mid` | `#2563eb` | Links, active states (blue-600) |
| `--color-border` | `#e5e7eb` | Hairline borders (gray-200) |
| `--color-border-strong` | `#d1d5db` | Dividers, table lines (gray-300) |

### Grade Tiers

| Grade | Token | Hex | Rationale |
|---|---|---|---|
| Gold | `--color-gold` | `#b45309` | Amber-700 — warm, earned authority |
| Silver | `--color-silver` | `#4b5563` | Gray-600 — neutral, competent |
| Bronze | `--color-bronze` | `#7c3aed` | Violet-600 — emerging, room to grow |
| Gold bg | `--color-gold-bg` | `#fef3c7` | Amber-100 |
| Silver bg | `--color-silver-bg` | `#f3f4f6` | Gray-100 |
| Bronze bg | `--color-bronze-bg` | `#ede9fe` | Violet-100 |

---

## Typography

Three-family system. Each family signals a distinct information layer.

### Heading — Newsreader (Serif editorial)
```css
font-family: 'Newsreader', Georgia, serif;
@import url('https://fonts.googleapis.com/css2?family=Newsreader:wght@400;500;600;700&display=swap');
```
Usage: Page title, section headings, pull quotes.
Mood: Trustworthy, editorial, longform journalism (NYT/The Pudding).

### UI — Public Sans (Geometric sans-serif)
```css
font-family: 'Public Sans', system-ui, sans-serif;
@import url('https://fonts.googleapis.com/css2?family=Public+Sans:wght@300;400;500;600;700&display=swap');
```
Usage: Body text, nav, labels, data values, buttons.
Mood: Government-grade clarity, US Web Design System origin.

### Mono — Fira Code (Technical metadata)
```css
font-family: 'Fira Code', 'Courier New', monospace;
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&display=swap');
```
Usage: Column names, ISO codes, version numbers, dataset IDs, scores.
Mood: Precise, auditable, machine-readable.

### Scale
| Level | Font | Size | Weight | Line-height |
|---|---|---|---|---|
| Display | Newsreader | 56px / 4.5vw | 700 | 1.05 |
| H1 | Newsreader | 40px | 700 | 1.15 |
| H2 | Newsreader | 28px | 600 | 1.2 |
| H3 | Public Sans | 18px | 600 | 1.3 |
| Body | Public Sans | 16px | 400 | 1.7 |
| Small | Public Sans | 14px | 400 | 1.6 |
| Caption | Public Sans | 12px | 400 | 1.5 |
| Mono data | Fira Code | 14px | 400 | 1.4 |

---

## Spacing

Base unit: 4px (Tailwind default).

| Scale | Value | Usage |
|---|---|---|
| `xs` | 4px | Icon gaps, tight labels |
| `sm` | 8px | Intra-card padding |
| `md` | 16px | Default gap |
| `lg` | 32px | Section inner padding |
| `xl` | 64px | Section separation |
| `2xl` | 96px | Hero vertical padding |

---

## Border Radius
- Cards: `8px` (rounded-lg) — not aggressive, institutional feel
- Badges: `4px` (rounded) — compact
- Buttons: `6px` (rounded-md)
- No full pill/rounded-full anywhere (too playful for civic tech)

---

## Shadows
```css
/* Card hover */
box-shadow: 0 2px 8px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);

/* Elevated card */
box-shadow: 0 4px 16px rgba(0,0,0,0.08);
```
No colored shadows. No glow effects.

---

## Motion
```css
transition: all 150ms ease-out;  /* default state changes */
transition: all 250ms ease-out;  /* hover/focus reveals */
```
`prefers-reduced-motion: reduce` → all transitions disabled.
No entrance animations on first paint (content-dense journalism pattern).

---

## Anti-patterns for this project
- No glassmorphism / backdrop-blur
- No gradient text
- No emoji icons (use Lucide SVG)
- No drop shadows with color
- No `border-radius > 12px` on structural elements
- No whitespace-first layouts (content density is a design goal)
- No inline `style=""` on HTML elements (project convention)
