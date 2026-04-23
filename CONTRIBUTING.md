# Guía de Contribución y Estilo (CONTRIBUTING.md)

¡Gracias por tu interés en mejorar la infraestructura de **Datos Abiertos NL 2026**! Este proyecto es un ecosistema técnico dual (Python Data Pipeline + Next.js UI) diseñado bajo un estricto rigor académico y una estética *Premium*.

Esta guía es vital tanto para ingenieros humanos como para **Agentes de Inteligencia Artificial** (AI Agents) que operen en este repositorio.

## 🛠️ Entorno de Desarrollo y Estilo de Código

### Ecosistema Python (Pipeline & Dashboard Analítico)
1. **Tipado Estricto**: Todo el código nuevo debe estar tipado (`typing`). El proyecto es compatible con `pyright`.
2. **Pandas Copy-on-Write (CoW)**: El proyecto asume el uso de Pandas 3.0+. Minimiza mutaciones en sitio (`inplace=True`) y adopta flujos inmutables.
3. **Formateo**: Utilizamos `ruff` (linting) y `black` (formateo). Antes de hacer *commit*, corre:
   ```bash
   ruff check --fix .
   black .
   ```
4. **Testing**: Todas las pruebas residen en la carpeta `pipeline/` con el patrón `test_*.py`. Ejecuta `pytest` antes de subir código.

### Ecosistema Next.js (Plataforma Pública)
1. **React Server Components**: Por defecto, utiliza Server Components. Agrega `"use client"` únicamente en componentes de hoja (leaf components) que requieran interactividad o estado (`useState`, `useEffect`, `framer-motion`).
2. **Shadcn UI & Tailwind**: Cualquier componente nuevo debe residir en `landing/components/ui/` y seguir los patrones de la utilidad `cn()` para mezcla de clases CSS.

## 🎨 Design System: "Glassmorphism Premium"

La plataforma de Next.js migró de un estilo de *dashboard* denso a una narrativa editorial de alto nivel. Si agregas o modificas UI, **debes** seguir estas reglas (vigiladas por el agente `ui-ux-pro-max` y `design-system-pro`):

1. **Jerarquía Tipográfica**:
   - **Títulos (Serif)**: Usa familias Serif (`font-serif`) elegantes para los `<h2>` y `<h3>`.
   - **Metadatos (Mono)**: Usa `font-mono`, `text-[10px]`, `tracking-widest` y `uppercase` para etiquetas técnicas y Eyebrows (ej. "ISO/IEC 25012:2008").
2. **Glassmorphism**:
   - Evita bloques de color sólido (ej. `bg-white`, `bg-gray-100`).
   - Usa fondos translúcidos: `bg-background/40`, `bg-midnight/5` mezclados con `backdrop-blur-md` o `backdrop-blur-lg`.
   - Aplica bordes finos y translúcidos: `border-border/40`, `border-teal/20`.
3. **Paleta Semántica Corporativa**:
   - **Midnight** (Primario / Fondos sutiles).
   - **Teal** (Acentos, interactividad, métricas Silver).
   - **Gold** (Premium, métricas Gold).
   - **Rose / Violet** (Alertas, métricas Bronze).
4. **Animaciones**:
   - Prefiere `framer-motion` o clases nativas fluidas (`transition-all duration-500 hover:-translate-y-1 hover:shadow-2xl`).

## 🤖 Interacción con Agentes IA (Multi-Agent System)

Este proyecto está dotado de habilidades de Inteligencia Artificial (Skills) ubicadas en `.agent/skills/`.

- **`AGENTS.md` / `GEMINI.md`**: Leídos obligatoriamente por los LLM (como Gemini, Claude) al iniciar contexto.
- **Workflow para IA**: Si eres una IA, antes de sugerir un cambio estructural, debes generar un `implementation_plan.md` (Artefacto), validarlo con el usuario humano, y proceder a crear los cambios sin romper los imports ni el flujo de UI ya establecido.

## 📦 Flujo de Trabajo (Git Workflow)

1. **Ramas (Branches)**: Crea ramas descriptivas (`feat/mejora-ranking`, `fix/metricas-nulas`).
2. **Commits**: Usa *Conventional Commits* (`feat:`, `fix:`, `docs:`, `refactor:`).
3. **Despliegue**: El código de la rama `main` se asume estable y listo para integrarse a Google Cloud Run o Vercel.
