---
name: quantitative-methodology-review
description: >
  Reviews academic LaTeX reports to guarantee they fully follow the
  quantitative-methodology workflow and APA 7 citation rules. Scans all files
  under @Documentacion/, extracts the research design, data-handling steps,
  statistical analysis, and results, then produces a checklist of missing or
  improvable methodological elements. Use when the user mentions "refine the
  argumentative report", "methodology check", "quantitative methodology", or
  "APA 7 compliance" for a LaTeX project.
---

# Quantitative Methodology Review

## Quick start

```bash
# From the repository root
claude-code run quantitative-methodology-review
```

The agent will:

1. Locate every `*.tex` file inside `@Documentacion/`.
2. Parse sections with the headings **Introducci\'on**, **Metodolog\'ia**,
   **Resultados**, **Discusi\'on**, **Conclusiones**.
3. Cross-reference LaTeX citations with `referencias.bib`.
4. Produce a markdown checklist (`methodology_review_report.md`) and a brief
   summary PDF.

---

## Workflow (checklist)

### 1. Gather artefacts

- [ ] `glob` -> `@Documentacion/**/*.tex`
- [ ] `read` -> `referencias.bib`
- [ ] (optional) Run `scripts/check_citations.py` to flag missing `\cite{}`
      keys.

### 2. Analyse methodological blocks

| Section | What to verify |
|---|---|
| **Planteamiento del problema** | Clear quantitative question, justification, relevance. |
| **Objetivos** | Specific, measurable, linked to variables. |
| **Hip\'otesis** | Formulated as null/alternative, testable with collected data. |
| **Dise\~no de estudio** | Type (experimental, correlacional, longitudinal), unit of analysis, timeline. |
| **Muestreo** | Population, sampling technique, power-analysis or justification of sample size. |
| **Instrumentos** | Software libraries, APIs, measurement scales, validation of instruments. |
| **Procedimientos** | Step-by-step pipeline (referencing exact code files/line ranges). |
| **An\'alisis de datos** | Statistical tests, assumptions checks, effect-size reporting, confidence intervals, handling of missing data. |
| **Resultados** | Tables/figures labelled per APA 7, include `\caption{}` and `\label{}`. |
| **Discusi\'on** | Comparison with literature, limitations, implications, future work. |
| **Conclusiones** | Direct answer to objectives, quantitative summary. |

### 3. APA 7 Compliance

- [ ] Every `\cite{}` matches an entry in `referencias.bib`.
- [ ] Bibliography sorted alphabetically, hanging indent, DOI/URL when
      available.
- [ ] Tables and figures follow APA style (title, note, proper numbering).
- [ ] Use of past tense for methods, present for established knowledge,
      future for recommendations.

### 4. Generate report

The agent creates `methodology_review_report.md` containing:

- **Checklist** with check/cross items.
- **Specific line-range references** for any missing or weak content
  (e.g., *"Add sampling-size justification in reporte_investigacion.tex
  lines 42--45"*).
- **Suggestions** for additional sections (e.g., *"Consider adding a
  data-quality assessment subsection under Metodologia"*).

Optionally, the agent renders the markdown to
`methodology_review_report.pdf` for easy sharing with the tutor.

### 5. Human-in-the-loop prompts

- If a citation is missing:
  *"Citation Author2022 not found in referencias.bib. Add it now?"*
- If a methodological element is absent:
  *"The sampling strategy is not described. Should I propose a standard
  simple random-sampling paragraph?"*

The agent **stops after each prompt** awaiting confirmation.

---

## Advanced features (see REFERENCE.md)

- **Batch mode** -- run the skill on multiple LaTeX projects by passing a
  root path argument.
- **Custom APA style** -- toggle `--style=apa6` for older requirements.
- **Export to Word** -- generate a `.docx` version via Pandoc (requires
  Pandoc installed on host).
