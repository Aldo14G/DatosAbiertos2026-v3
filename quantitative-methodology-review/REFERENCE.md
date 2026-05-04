# REFERENCE.md -- Quantitative Methodology Review (Extended)

This document provides the full reference checklist, APA 7 formatting tips,
and advanced configuration options for the `quantitative-methodology-review`
skill. It is intended as a companion to `SKILL.md`.

---

## Table of Contents

1. [Full Methodology Checklist](#1-full-methodology-checklist)
2. [APA 7 Formatting Reference](#2-apa-7-formatting-reference)
3. [LaTeX-Specific Rules](#3-latex-specific-rules)
4. [Statistical Reporting Standards](#4-statistical-reporting-standards)
5. [Common Pitfalls](#5-common-pitfalls)
6. [Batch Mode Configuration](#6-batch-mode-configuration)
7. [Export Options](#7-export-options)

---

## 1. Full Methodology Checklist

### 1.1 Title Page

- [ ] Full title (max 12 words recommended).
- [ ] Author name, institutional affiliation, date.
- [ ] Running head (if required by institution).

### 1.2 Abstract

- [ ] 150--250 words.
- [ ] States purpose, method, key results, and conclusion.
- [ ] Keywords line (3--5 terms, lowercase, separated by commas).
- [ ] No citations in the abstract (APA 7 recommendation).

### 1.3 Introduction

- [ ] Opens with a broad statement about the research area.
- [ ] Narrows to the specific problem.
- [ ] States research questions explicitly.
- [ ] Cites relevant literature (minimum 5 peer-reviewed sources).
- [ ] Ends with purpose statement or hypotheses.

### 1.4 Literature Review (if separate from Introduction)

- [ ] Organized thematically, not chronologically.
- [ ] Each paragraph cites at least one source.
- [ ] Identifies gaps in existing research.
- [ ] Builds toward the rationale for the current study.

### 1.5 Methodology

#### 1.5.1 Research Design

- [ ] Explicitly names the design (e.g., descriptive, correlational,
      quasi-experimental, longitudinal).
- [ ] Justifies why this design answers the research questions.
- [ ] States the unit of analysis.

#### 1.5.2 Population and Sampling

- [ ] Defines the target population.
- [ ] Describes the sampling technique (probability vs. non-probability).
- [ ] Reports sample size with justification (power analysis, census,
      convenience rationale).
- [ ] Describes inclusion/exclusion criteria.

#### 1.5.3 Instruments / Data Sources

- [ ] Lists all instruments, software, APIs, or data sources used.
- [ ] Reports validity and reliability evidence for each instrument.
- [ ] For computational instruments: references specific code files
      and version numbers.

#### 1.5.4 Variables

- [ ] Lists all variables with their operational definitions.
- [ ] Specifies measurement scale (nominal, ordinal, interval, ratio).
- [ ] Identifies independent, dependent, and control variables.

#### 1.5.5 Procedures

- [ ] Step-by-step description of data collection.
- [ ] References code files with line ranges where applicable.
- [ ] Describes ethical considerations (IRB approval, informed consent,
      data anonymization).

#### 1.5.6 Data Analysis Plan

- [ ] Lists all statistical techniques to be used.
- [ ] States software and version (e.g., Python 3.13, pandas 2.2).
- [ ] Describes how assumptions will be checked.
- [ ] States the significance level (alpha).

### 1.6 Results

- [ ] Presents findings in the order of the research questions.
- [ ] All tables and figures are numbered and captioned.
- [ ] Reports descriptive statistics before inferential statistics.
- [ ] Includes effect sizes where applicable.
- [ ] Does not interpret results (save for Discussion).

### 1.7 Discussion

- [ ] Restates key findings in relation to hypotheses.
- [ ] Compares results with prior literature (cites specific studies).
- [ ] Discusses practical and theoretical implications.
- [ ] Acknowledges limitations honestly.
- [ ] Proposes future research directions.

### 1.8 Conclusions

- [ ] Directly answers each research question with quantitative evidence.
- [ ] Summarizes the main contribution of the study.
- [ ] Avoids introducing new information.

### 1.9 References

- [ ] Every in-text citation has a corresponding reference entry.
- [ ] Every reference entry is cited at least once in the text.
- [ ] Formatted per APA 7 (hanging indent, DOI as hyperlink).

---

## 2. APA 7 Formatting Reference

### 2.1 In-Text Citations

| Situation | Format |
|---|---|
| One author | `\parencite{smith2020}` -> (Smith, 2020) |
| Two authors | `\parencite{smith2020}` -> (Smith & Jones, 2020) |
| Three+ authors | `\parencite{smith2020}` -> (Smith et al., 2020) |
| Narrative | `\textcite{smith2020}` -> Smith (2020) |
| Direct quote | `\parencite[p.~45]{smith2020}` -> (Smith, 2020, p. 45) |

### 2.2 Reference List Formatting

```bibtex
@article{vetro2016,
  author  = {Vetr\`o, Antonio and others},
  title   = {Open Data Quality Measurement Framework},
  journal = {Journal of the American Society for Information Science
             and Technology},
  year    = {2016},
  volume  = {67},
  number  = {9},
  pages   = {2082--2097},
  doi     = {10.1002/asi.23604},
}
```

Rules:
- Use `doi = {10.xxxx/...}` (no "https://doi.org/" prefix; biblatex-apa
  adds it automatically).
- For URLs without DOI: use `url = {...}` and `urldate = {2026-05-01}`.
- Capitalize only the first word of titles (sentence case).
- Journal names in title case.

### 2.3 Tables (APA 7)

```latex
\begin{table}[h!]
\centering
\caption{Descriptive Statistics by Dimension}
\label{tab:descriptives}
\begin{tabular}{lccc}
\toprule
\textbf{Variable} & \textbf{M} & \textbf{SD} & \textbf{n} \\
\midrule
Completitud & 85.09 & 24.47 & 288 \\
Exactitud   & 92.35 &  5.67 & 288 \\
\bottomrule
\end{tabular}

\medskip
\noindent\textit{Note.} M = mean; SD = standard deviation.
\end{table}
```

Key rules:
- Title above the table, in italics (handled by `\caption{}`).
- No vertical lines.
- Use `\toprule`, `\midrule`, `\bottomrule` (from `booktabs`).
- Notes below the table.

### 2.4 Figures (APA 7)

```latex
\begin{figure}[h!]
\centering
\includegraphics[width=0.85\textwidth]{figures/histogram.png}
\caption{Distribution of global quality scores for 288 resources.}
\label{fig:histogram}
\end{figure}
```

Key rules:
- Caption below the figure.
- Figures must be interpretable in grayscale (or use color-blind-safe
  palettes).
- Reference every figure in the text before it appears.

---

## 3. LaTeX-Specific Rules

### 3.1 Encoding

- Use `\usepackage[utf8]{inputenc}` and `\usepackage[T1]{fontenc}`.
- For maximum portability on Windows, prefer LaTeX accent commands
  (`\'o`, `\'e`, `\~n`) over raw Unicode characters.
- **Never** let PowerShell re-encode `.tex` files. Use Python scripts
  for any programmatic text replacement.

### 3.2 Bibliography Engine

- Use `biblatex` with `biber` backend (not BibTeX).
- Load with: `\usepackage[style=apa,backend=biber,language=spanish]{biblatex}`
- Compile sequence: `pdflatex` -> `biber` -> `pdflatex` -> `pdflatex`.

### 3.3 Spanish Language Support

```latex
\usepackage[spanish,es-tabla]{babel}
```

The `es-tabla` option changes "Table" to "Tabla" and "Figure" stays as
configured by the caption package.

### 3.4 Common LaTeX Pitfalls

| Problem | Solution |
|---|---|
| `Unicode character not set up` | Use `$\sigma$` instead of raw sigma |
| `No driver for standard` | Change `@techreport` to `@misc` in `.bib` |
| Double-encoded accents | Rewrite file with LaTeX accent commands |
| BOM in `.tex` files | Open with `encoding='utf-8'` (no `-sig`) in Python |

---

## 4. Statistical Reporting Standards

### 4.1 Descriptive Statistics

Always report:
- Mean ($M$ or $\mu$)
- Standard deviation ($SD$ or $\sigma$)
- Sample size ($n$ or $N$)
- Minimum and maximum values
- Median when distribution is skewed

### 4.2 Inferential Statistics

When applicable, report:
- Test statistic with degrees of freedom: $t(286) = 3.42$
- Exact $p$-value: $p = .001$ (not $p < .05$)
- Effect size: Cohen's $d$, $\eta^2$, $r$
- Confidence interval: 95\% CI $[2.15, 4.69]$

### 4.3 Formatting Numbers

- Use one decimal place for percentages: 65.6\%
- Use two decimal places for correlations, means, SDs: $M = 88.83$
- Use three decimal places for $p$-values: $p = .003$
- Leading zero for values that can exceed 1.00: $M = 0.85$
- No leading zero for values bounded by 1.00: $p = .003$, $r = .72$

---

## 5. Common Pitfalls

### 5.1 Methodological

1. **Confusing population with sample.** The population is the entire
   set; the sample is what you actually measured.
2. **Missing operational definitions.** Every variable must have a
   formula or measurement procedure.
3. **Claiming causation from correlation.** Unless the design is
   experimental with random assignment, use associational language.
4. **Ignoring assumptions.** Report normality checks, homogeneity of
   variance, or explain why they are not applicable.

### 5.2 Writing

1. **Passive voice overuse.** APA 7 encourages active voice.
2. **Anthropomorphizing data.** Say "the results indicate" not "the
   data show that they prefer."
3. **Citing secondary sources.** Always cite the original study.
4. **Inconsistent tense.** Past for your methods and results; present
   for established facts; future for recommendations.

### 5.3 Citation

1. **Self-plagiarism.** Always cite your own prior work.
2. **String citations.** Avoid (Author1, 2020; Author2, 2019; Author3,
   2021) without explaining the relevance of each.
3. **Over-reliance on web sources.** Prefer peer-reviewed journals.

---

## 6. Batch Mode Configuration

To run the skill across multiple LaTeX projects:

```bash
# Pass a root directory containing multiple Documentacion/ folders
claude-code run quantitative-methodology-review --root /path/to/projects/
```

The agent will discover each `Documentacion/` subdirectory and generate
a separate `methodology_review_report.md` for each one.

---

## 7. Export Options

### 7.1 Markdown (default)

Output: `methodology_review_report.md`

### 7.2 PDF

Requires `pdflatex` and `biber` in PATH:

```bash
pandoc methodology_review_report.md -o methodology_review_report.pdf
```

### 7.3 Word (DOCX)

Requires Pandoc:

```bash
pandoc methodology_review_report.md -o methodology_review_report.docx
```

---

## Changelog

| Version | Date | Changes |
|---|---|---|
| 1.0.0 | 2026-05-03 | Initial release with full checklist and APA 7 rules. |
