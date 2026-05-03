# Design Tokens — DatosAbiertos NL 2026 Landing & Dashboard

Generated from UI/UX Pro Max skill. Civic tech / data journalism aesthetic.
Matches both Next.js (port 3000) and Streamlit (port 8501) exactly.

---

## Color Palette (Midnight / Teal / Gold / Rose)

| Token | Hex | Usage |
|---|---|---|
| `--color-background` (Light) | `#f9f8f5` | Page background (warm off-white, print feel) |
| `--color-background` (Dark) | `#0f1c2e` | Midnight navy background |
| `--color-foreground` (Light) | `#0d1117` | Primary body text (near-black) |
| `--color-foreground` (Dark) | `#faf6ee` | Primary body text (cream) |
| `--color-primary` (Teal) | `#2a7a6f` | Positive indicators, primary accents |
| `--color-primary-light` (Teal L)| `#3aa895` | Teal light for dark mode |
| `--color-gold` | `#c8973a` | Structures, secondary accents |
| `--color-gold-light` | `#e4b96a` | Gold light for dark mode |
| `--color-rose` | `#b85c6e` | Alerts, critical issues |
| `--color-rose-light` | `#d4738a` | Rose light for dark mode |
| `--color-border` (Light) | `rgba(200,151,58,0.25)` | Gold-tinted borders |
| `--color-border` (Dark) | `rgba(255,255,255,0.1)` | Subtle white borders |
| `--color-card` (Light) | `#ffffff` | Pure white cards |
| `--color-card` (Dark) | `rgba(255,255,255,0.04)` | Glass cards in dark mode |

### Grade Tiers (ISO 25012)
| Grade | Base Color |
|---|---|
| Gold | `--color-gold` / `--color-gold-light` |
| Silver | `--color-foreground` (with opacity) |
| Bronze | `--color-rose` / `--color-rose-light` |

---

## Typography

Three-family system. Each family signals a distinct information layer.

### Heading — Playfair Display (Serif editorial)
```css
font-family: 'Playfair Display', Georgia, serif;
```
Usage: Page title, section headings, high-impact metrics.
Mood: Trustworthy, editorial, institutional authority.

### UI — DM Sans (Geometric sans-serif)
```css
font-family: 'DM Sans', system-ui, sans-serif;
```
Usage: Body text, nav, labels, buttons.
Mood: Modern, clean, highly legible on screens.

### Mono — DM Mono (Technical metadata)
```css
font-family: 'DM Mono', monospace;
```
Usage: Data values, KPIs, small labels, version numbers.
Mood: Precise, auditable, machine-readable.

---

## Layout & Effects
- **Glassmorphism:** Used sparingly in dark mode (`rgba(255,255,255,0.04)` with `backdrop-blur`).
- **Border Radius:** Variable, but cohesive. Hero components use `.rounded-2xl` (16px), cards use 12px or 14px (`--radius` base 0.75rem in Next).
- **Shadows:** Soft, large spread shadows on hover (`shadow-md` to `shadow-lg`). No harsh colored glows.
