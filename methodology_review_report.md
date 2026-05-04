# Methodology Review Report --- DatosAbiertos2026-v3

**Fecha de auditoría:** 2026-05-03  
**Archivos analizados:**
- `Documentacion/reporte_investigacion.tex` (455 líneas)
- `Documentacion/protocolo-investigacion.tex` (370 líneas)
- `Documentacion/referencias.bib` (127 líneas, 13 entradas)

---

## 1. Citas (check_citations.py)

| Indicador | Resultado |
|---|---|
| Citas resueltas | 12 / 12 |
| Citas faltantes | 0 |
| Entradas bib sin usar | 1 (`lgtaip2015` --- citada solo en protocolo, no en reporte) |
| **Veredicto** | OK |

---

## 2. Checklist Metodológico

### 2.1 Planteamiento del problema

| Criterio | Protocolo | Reporte | Estado |
|---|---|---|---|
| Pregunta cuantitativa clara | L92 | L129--137 | OK |
| Justificación (brecha en la literatura) | L78--84 | L98--119 | OK |
| Relevancia (por qué este estudio importa) | L84 | L98--103 | OK --- pero el reporte usa la frase genérica "recurso estratégico" sin citar fuente |

**Hallazgo R-01 (reporte L98):** La frase _"Los datos abiertos gubernamentales son considerados un recurso estratégico"_ carece de cita. Agregar `\parencite{bernerslee2006}` o reformular.

### 2.2 Objetivos

| Criterio | Protocolo | Reporte | Estado |
|---|---|---|---|
| Objetivo general | L125 | NO PRESENTE | FALTANTE |
| Objetivos específicos | L129--139 | NO PRESENTE | FALTANTE |

**Hallazgo R-02 (reporte):** El reporte carece de una sección de objetivos. En metodología cuantitativa, los objetivos deben preceder o acompañar a las preguntas de investigación para que el lector verifique la coherencia entre ambos.

### 2.3 Hipótesis

| Criterio | Protocolo | Reporte | Estado |
|---|---|---|---|
| Formulación H1 | L109 | L143--144 | OK |
| Formulación H2 (ANOVA) | L111 | NO PRESENTE | FALTANTE --- el reporte omite H2 y H3 |
| Formulación H3 (completitud) | L113 | NO PRESENTE | FALTANTE |
| Formulación H4 | L115 | L145--147 | OK |
| Contrastación explícita | --- | L250--253 (H1), L298--301 (H4) | PARCIAL --- H2 y H3 no se contrastan |

**Hallazgo R-03:** El protocolo define 4 hipótesis (H1--H4). El reporte solo contrasta H1 y H4. Debe incluir una nota sobre H2 y H3: por qué no se ejecutó el ANOVA (H2) y si la completitud tuvo o no el mayor peso relativo en el score (H3).

### 2.4 Diseño de estudio

| Criterio | Protocolo | Reporte | Estado |
|---|---|---|---|
| Tipo de diseño | Implícito (descriptivo, transversal) | NO DECLARADO | FALTANTE |
| Unidad de análisis | L167 (recurso individual) | L237 | OK |
| Temporalidad | L342--362 (cronograma) | NO DECLARADO | FALTANTE |

**Hallazgo R-04 (reporte):** El reporte no declara el tipo de diseño. Insertar una línea: _"El estudio adoptó un diseño descriptivo, transversal y no experimental."_

### 2.5 Muestreo

| Criterio | Protocolo | Reporte | Estado |
|---|---|---|---|
| Población definida | L148 | NO DECLARADA en reporte | FALTANTE |
| Tipo de muestreo | L152 (censal) | L235 (censal) | OK |
| Tamaño justificado | L152 (procesable computacionalmente) | L237 (288 recursos) | OK |
| Criterios inclusión/exclusión | L174--176 | L239--240 (parcial) | PARCIAL --- falta límite de 50 MB y dominios autorizados |

### 2.6 Instrumentos

| Criterio | Protocolo | Reporte | Estado |
|---|---|---|---|
| Software y versión | L226 (Python 3.13+) | L74, L178 | OK |
| Archivos de código referenciados | L233--237 | L182--191 | OK |
| Validez de contenido | L242 | NO DECLARADA en reporte | FALTANTE |
| Confiabilidad | L242 | L194--196 | OK |

**Hallazgo R-05 (reporte):** El reporte no menciona la validez de contenido (alineación ISO + DAMA). El protocolo sí la documenta (L242). Agregar un párrafo.

### 2.7 Procedimientos

| Criterio | Protocolo | Reporte | Estado |
|---|---|---|---|
| Pasos de recolección | L232--237 | L181--192 | OK |
| Referencia a código con líneas | Parcial | NO --- solo filenames | Mejorable |

### 2.8 Análisis de datos

| Criterio | Protocolo | Reporte | Estado |
|---|---|---|---|
| Descriptivos declarados | L321 | L249--253, tablas 3--4 | OK |
| Inferenciales declarados | L321 (ANOVA, t-test, OLS) | NO EJECUTADOS | INCONSISTENCIA |
| Supuestos de normalidad | L323 | NO VERIFICADOS | FALTANTE |

**Hallazgo R-06:** El protocolo promete ANOVA, t-test y OLS (L321). El reporte no ejecuta ninguna prueba inferencial. Debe incluirse una nota en la sección de Limitaciones o redactar la contrastación de H2 con análisis descriptivo por organización (que ya existe en la Figura 4).

### 2.9 Resultados

| Criterio | Reporte | Estado |
|---|---|---|
| Tablas numeradas con `\caption{}` y `\label{}` | Tablas 1--4 | OK |
| Figuras numeradas con `\caption{}` y `\label{}` | Figuras 1--4 | OK |
| Figuras referenciadas antes de aparecer | L255, L270, L305, L353 | OK |
| Nota bajo tablas (APA 7) | L230 | OK |

### 2.10 Discusión

| Criterio | Reporte | Estado |
|---|---|---|
| Comparación con literatura | L375 (Vetrò), L381 (Neumaier) | OK |
| Contraste con estudio previo | L394 (Alanís 2024) | OK |
| Limitaciones | L404--412 (3 limitaciones) | OK |
| Trabajo futuro | NO PRESENTE | FALTANTE |

**Hallazgo R-07:** La sección de discusión carece de un párrafo sobre trabajo futuro (evaluación longitudinal, extensión a otros estados, integración de IA semántica).

### 2.11 Conclusiones

| Criterio | Reporte | Estado |
|---|---|---|
| Respuesta directa a cada pregunta | PARCIAL --- responde PE1, PE3, PE4 pero no PE2 | PARCIAL |
| Resumen cuantitativo | L420--421 | OK |
| Evita información nueva | L445--447 introduce "evaluaciones longitudinales futuras" | Borderline |

---

## 3. APA 7 Compliance

| Criterio | Estado | Nota |
|---|---|---|
| Todas las `\cite{}` resueltas | OK | 0 faltantes |
| DOI presentes donde aplica | OK | `vetro2016`, `neumaier2016`, `wang1996` tienen DOI |
| Tablas: `booktabs`, sin líneas verticales | OK | Todas usan `\toprule/\midrule/\bottomrule` |
| Figuras: caption debajo | OK | Las 4 figuras cumplen |
| Tiempos verbales correctos | PARCIAL | Métodos en pasado: OK. L445--447 mezcla presente con futuro |
| `@standard` y `@legislation` en bib | ADVERTENCIA | `biblatex-apa` no tiene driver nativo para estos tipos; considerar `@misc` |

---

## 4. Redacción: Frases genéricas de IA detectadas

| Línea(s) | Frase detectada | Problema | Corrección propuesta |
|---|---|---|---|
| L98 | "recurso estratégico para la transparencia" | Muletilla sin cita | Reformular con referencia concreta |
| L340 | "áreas de mayor oportunidad de mejora" | Eufemismo corporativo | Decir "dimensiones con puntajes deficientes" |
| L384--385 | "limita el potencial de reutilización por parte de actores externos" | Frase excesivamente larga y vaga | Decir "dificulta que investigadores y periodistas utilicen estos datos" |
| L430 | "oportunidades de mejora significativas" | Redundancia con L340 | Usar "deficiencias documentadas" |
| L445--447 | "establece una línea base ... que podrá utilizarse en evaluaciones longitudinales futuras para medir el impacto de las políticas" | "medir el impacto" es frase genérica | Decir "para verificar si las dependencias mejoran sus procesos de publicación" |

---

## 5. Inconsistencias entre protocolo y reporte

| # | Descripción | Protocolo | Reporte |
|---|---|---|---|
| I-01 | H2 y H3 existen en protocolo pero no en reporte | L111, L113 | Ausentes |
| I-02 | Protocolo promete ANOVA, t-test, OLS | L321 | No se ejecutaron |
| I-03 | Protocolo menciona GeoJSON y XML | L132, L174 | Reporte dice solo CSV, JSON, XLSX (L236) |
| I-04 | Protocolo usa acentos UTF-8 nativos | Todo el archivo | Reporte usa comandos LaTeX (`\'o`) |
| I-05 | Protocolo menciona "Gemini 2.5 Flash" (L246) | L246 | Reporte dice "Vertex AI (Google Gemini)" sin versión (L410) |

---

## 6. Acciones requeridas (prioridad)

| Prioridad | Acción | Archivo | Líneas |
|---|---|---|---|
| ALTA | Agregar nota sobre H2/H3 no contrastadas | reporte | Sección 2 o Limitaciones |
| ALTA | Eliminar frases genéricas de IA (tabla §4) | reporte | L98, L340, L384, L430, L447 |
| ALTA | Declarar tipo de diseño ("descriptivo, transversal, no experimental") | reporte | Antes de §3.1 |
| MEDIA | Agregar subsección de objetivos | reporte | Entre §1 y §2 |
| MEDIA | Mencionar validez de contenido del instrumento | reporte | §3.2 |
| MEDIA | Agregar párrafo de trabajo futuro en Discusión | reporte | Después de §5.3 |
| MEDIA | Unificar formatos (GeoJSON/XML vs solo CSV/JSON/XLSX) entre documentos | ambos | protocolo L132, reporte L236 |
| BAJA | Cambiar `@standard` y `@legislation` a `@misc` en bib | referencias.bib | L35, L42 |
| BAJA | Unificar encoding (protocolo usa UTF-8, reporte usa LaTeX commands) | ambos | Cosmético --- no afecta compilación |

---

**Veredicto global:** El reporte tiene una estructura sólida y los datos numéricos son consistentes con el CSV. Los hallazgos principales son: (1) falta la sección de objetivos, (2) las hipótesis H2 y H3 no se contrastan, (3) hay frases genéricas que debilitan el registro académico.
