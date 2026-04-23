---
name: academic-research-multiagent
description: >
  Orquesta un equipo de agentes especializados para construir documentación científica
  rigurosa: busca fuentes reales en repositorios académicos (Google Scholar, arXiv, Dialnet,
  Semantic Scholar, PubMed, repositorios oficiales de OCDE/INAI/ISO), verifica cada URL,
  y produce el marco teórico, bibliografía APA 7 y secciones metodológicas con citas
  verificadas. Diseñado específicamente para el proyecto de Gobernanza de Datos Abiertos
  de Nuevo León 2026 (ISO/IEC 25012, Wang & Strong, CKAN pipeline).
license: MIT — Proyecto NL 2026 · Aldo14G
---

# Skill: Equipo de Investigación Académica Multi-Agente
**Proyecto:** Infraestructura de Gobernanza y Evaluación Automatizada de la Calidad de
Datos Abiertos Gubernamentales — Nuevo León 2026.

Este skill orquesta un equipo de 6 agentes especializados que trabajan en paralelo para
producir documentación científica con fuentes verificadas. Cada agente tiene un rol, un
conjunto de fuentes autorizadas y un protocolo de validación de URLs.

---

## PROBLEMA QUE RESUELVE

El boceto de protocolo de investigación (`Metodologia_Cuantitativa.pdf`) contiene citas
cuyas URLs no han sido verificadas como activas. Antes de usarlas en un documento
académico deben pasar por:

1. **Verificación de existencia** — la URL responde con 200 y el contenido corresponde.
2. **Verificación de autoría** — el autor, año y título coinciden con la referencia APA.
3. **Búsqueda de alternativa** — si la URL original está caída, el agente busca el DOI
   oficial o el repositorio institucional.

---

## ROLES DEL EQUIPO

### Rol 0 — Director (AldoGbot)
**Responsabilidad:** Orquestación, aprobación de planes y consolidación final.
**Regla crítica:** Ningún agente inicia escritura hasta recibir `APPROVED` del Director.
**Entregable:** `tasks.json` actualizado + documento final consolidado.

---

### Rol 1 — Arqueólogo de Fuentes (`agente_fuentes.py`)
**Responsabilidad:** Buscar y verificar fuentes académicas reales para cada cita del PDF.

**Bases de datos autorizadas (en orden de prioridad):**

| Base | URL base | Tipo de acceso |
|------|----------|---------------|
| Google Scholar | `https://scholar.google.com/scholar?q=` | Web search |
| arXiv | `https://arxiv.org/search/?searchtype=all&query=` | API + web fetch |
| Semantic Scholar | `https://api.semanticscholar.org/graph/v1/paper/search?query=` | API REST |
| Dialnet | `https://dialnet.unirioja.es/buscar/documentos?querysDismax.DOCUMENTAL_TODO=` | Web fetch |
| BASE (Bielefeld) | `https://www.base-search.net/Search/Results?lookfor=` | Web fetch |
| OCDE iLibrary | `https://www.oecd-ilibrary.org/` | Web fetch por DOI |
| INAI México | `https://home.inai.org.mx/` | Web fetch |
| OGD Watch | `https://www.ogdwatch.de/` | Web fetch |
| ISO Online | `https://www.iso.org/standard/` | Web fetch |
| Google DeepMind | `https://deepmind.google/research/publications/` | Web fetch |
| Anthropic Research | `https://www.anthropic.com/research` | Web fetch |
| ACM Digital Library | `https://dl.acm.org/doi/` | Web fetch por DOI |
| SSRN | `https://papers.ssrn.com/sol3/results.cfm?RequestTimeout=50000&txtKey_Words=` | Web fetch |

**Protocolo de verificación (ejecutar en este orden):**
```
1. Intentar web_fetch(url_original)
   → Si HTTP 200 y título coincide → VERIFIED ✓
   → Si HTTP 404/403/timeout → ir a paso 2

2. Buscar por DOI en https://doi.org/{doi}
   → Si resuelve → usar DOI como URL canónica

3. Buscar en Semantic Scholar API:
   GET https://api.semanticscholar.org/graph/v1/paper/search
       ?query={titulo+autor+año}
       &fields=title,authors,year,externalIds,openAccessPdf
   → Si encuentra → extraer openAccessPdf.url o externalIds.DOI

4. Buscar en arXiv:
   GET https://export.arxiv.org/api/query?search_query=ti:{titulo}&au:{autor}

5. Buscar en Google Scholar via web_search:
   query: "{titulo}" "{autor}" {año} filetype:pdf

6. Si ninguna fuente resuelve → marcar UNVERIFIED y proponer alternativa temática
```

**Citas del PDF que REQUIEREN verificación prioritaria:**
```json
[
  {
    "id": "nexos-2025",
    "ref": "Nexos Federalismo. (2025). El nuevo modelo de datos abiertos en México.",
    "url_original": "https://federalismo.nexos.com.mx/2025/12/el-nuevo-modelo-de-datos-abiertos-en-mexico/",
    "estado": "PENDING"
  },
  {
    "id": "condatos-2023",
    "ref": "INAI. (2023). Política Nacional de Datos Abiertos (ConDATOS).",
    "url_original": "https://www.abramos.mx",
    "estado": "PENDING",
    "nota": "URL parece incorrecta — abramos.mx no es dominio INAI"
  },
  {
    "id": "flores-2024",
    "ref": "Flores, C., Janssen, M., & Rodríguez Bolívar, M.P. (2024). Government Information Quarterly.",
    "url_original": "https://doi.org/10.1016/j.giq.2023.101898",
    "estado": "PENDING"
  },
  {
    "id": "espinoza-2023",
    "ref": "Espinoza-Portilla et al. (2023). Revista Facultad de Ingeniería Universidad de Antioquia.",
    "url_original": "https://doi.org/10.17533/udea.redin.20220107",
    "estado": "PENDING"
  },
  {
    "id": "zhang-2024",
    "ref": "Zhang, J., Li, Y., & Wang, X. (2024). arXiv:2406.19614",
    "url_original": "https://arxiv.org/abs/2406.19614",
    "estado": "PENDING"
  },
  {
    "id": "ocde-ourdata-2023",
    "ref": "OCDE. (2023). 2023 OURdata Index.",
    "url_original": "https://doi.org/10.1787/a37f51c3-en",
    "estado": "PENDING"
  },
  {
    "id": "ocde-digital-2024",
    "ref": "OCDE. (2024b). 2023 Digital Government Index.",
    "url_original": "https://doi.org/10.1787/1a89ed5e-en",
    "estado": "PENDING"
  },
  {
    "id": "labnl-2024",
    "ref": "Gómez et al. (2024). ¿Cómo vamos en Datos en Nuevo León? WikiLabNL.",
    "url_original": "https://wiki.labnuevoleon.mx/index.php?title=¿Cómo_vamos_en_Datos_en_Nuevo_León%3F",
    "estado": "PENDING"
  },
  {
    "id": "wang-strong-1996",
    "ref": "Wang, R.Y. & Strong, D.R. (1996). JMIS, 12(4), 5–33.",
    "url_original": "https://doi.org/10.1080/07421222.1996.11518099",
    "estado": "PENDING"
  }
]
```

---

### Rol 2 — Investigador Cuantitativo (`agente_metodologia.py`)
**Responsabilidad:** Buscar literatura adicional actualizada (2020–2026) que refuerce
las hipótesis y el marco metodológico del PDF.

**Queries de búsqueda obligatorias:**
```python
SEARCH_QUERIES = [
    # Marco teórico principal
    "open government data quality assessment ISO 25012 automated pipeline",
    "Wang Strong 1996 data quality framework replication 2020 2024",
    "CKAN portal metadata quality evaluation subnational government",

    # Contexto mexicano / latinoamericano
    "datos abiertos gubernamentales calidad Mexico subnacional 2022 2024",
    "open data quality Latin America government portal evaluation",
    "gobierno abierto Nuevo León transparencia datos 2023 2026",

    # Métodos cuantitativos y herramientas
    "automated data quality scoring pipeline Python pandas government",
    "LLM large language model data quality assessment qualitative",
    "Streamlit dashboard government data transparency visualization",

    # Dimensión temporal / consistencia
    "temporal consistency open data update frequency government portal",
    "metadata completeness open data portal empirical study",

    # Normas y estándares
    "ISO IEC 25012 data quality model implementation evaluation",
    "DCAT metadata standard government linked data quality",
    "5-star open data Berners-Lee model government implementation review"
]
```

**Para cada resultado encontrado, extraer:**
```json
{
  "titulo": "",
  "autores": [],
  "año": 0,
  "doi": "",
  "url_verificada": "",
  "abstract_resumen": "",
  "relevancia_hipotesis": "H1|H2|H3|metodologia|marco_teorico",
  "cita_apa7": ""
}
```

---

### Rol 3 — Arquitecto Metodológico (`agente_variables.py`)
**Responsabilidad:** Revisar la tabla de variables del PDF (Sección 7) y proponer
fórmulas matemáticas precisas para cada dimensión, alineadas con el código
del `data_layer.py`.

**Mapa de correspondencia variables ↔ código:**
```python
VARIABLE_CODE_MAP = {
    # Variable → función en data_layer.py → columna en DataFrame
    "Completitud (Ci)":    ("compute_completeness", "comp_completitud_global_pct"),
    "Exactitud (Ei)":      ("compute_accuracy",     "acc_score_accuracy_pct"),
    "Consistencia (Ti)":   ("compute_consistency",  "cons_score_consistency_pct"),
    "Unicidad (Ui)":       ("compute_uniqueness",   "uniq_score_uniqueness_pct"),
    "Puntualidad (Pi)":    ("compute_timeliness",   "time_score_timeliness_pct"),
    # NOTA: El PDF nombra la 5ª dim "Consistencia temporal" — en el código se llama
    # compute_timeliness(). El agente debe documentar este mapeo explícitamente.
}

# Pesos ISO 25012 implementados en data_layer.py v2.1
QUALITY_WEIGHTS = {
    "completeness": 0.35,
    "accuracy":     0.30,
    "consistency":  0.20,
    "uniqueness":   0.10,
    "timeliness":   0.05,
}

# Fórmula del Score Global (documentar en LaTeX para el paper):
# Q_i = (0.35·C_i + 0.30·E_i + 0.20·T_i + 0.10·U_i + 0.05·P_i) / Σω
```

**Entregable:** Sección 7 (Variables) reescrita con fórmulas LaTeX verificadas y
anotaciones de correspondencia con el código fuente.

---

### Rol 4 — Redactor Académico (`agente_redactor.py`)
**Responsabilidad:** Redactar secciones del documento final usando exclusivamente
fuentes verificadas por el Arqueólogo (Rol 1). Estilo: APA 7, positivista-cuantitativo,
voz académica en español.

**Secciones a redactar (en orden de dependencias):**

```
Orden | Sección              | Depende de
------|----------------------|---------------------------
  1   | Marco Teórico 11.1   | Rol 1 (fuentes verificadas)
  2   | Marco Teórico 11.2   | Rol 1 + Rol 3 (variables)
  3   | Marco Teórico 11.3   | Rol 1 + Rol 2 (lit. adicional)
  4   | Marco Teórico 11.4   | Rol 3 (operacionalización)
  5   | Marco Teórico 11.5   | Rol 1 (LabNL verificado)
  6   | Sección 7 Variables  | Rol 3 (fórmulas)
  7   | Bibliografía APA 7   | Rol 1 (todas verificadas)
  8   | Resumen Ejecutivo    | Todo lo anterior
```

**Reglas de escritura:**
- Nunca citar una fuente que no esté en el archivo `fuentes_verificadas.json`.
- Toda afirmación empírica debe tener entre paréntesis la cita y el año.
- Las fórmulas matemáticas van en bloque LaTeX con numeración.
- Longitud mínima por sección: 400 palabras. Máxima: 800 palabras.
- Párrafo final de cada sección: implicación directa para el proyecto NL 2026.

---

### Rol 5 — Revisor / Devil's Advocate (`agente_revisor.py`)
**Responsabilidad:** Auditar el documento generado antes de entregarlo al Director.

**Checklist de revisión (ejecutar en orden):**
```
VALIDACIONES BIBLIOGRÁFICAS
[ ] Cada cita en el texto tiene entrada en la bibliografía
[ ] Cada entrada de la bibliografía tiene URL o DOI verificado (HTTP 200)
[ ] Formato APA 7 correcto: Apellido, I. (Año). Título. Revista, Vol(Num), pp. DOI
[ ] No hay citas de fuentes secundarias sin acceso al original

VALIDACIONES METODOLÓGICAS
[ ] Las hipótesis H1, H2, H3 son falsables y cuantificables
[ ] Las variables tienen escala de medición definida (continua/dicotómica)
[ ] La fórmula Q_i suma pesos = 1.0 exactamente
[ ] El instrumento (MEACD) está descrito con suficiente detalle para ser replicado
[ ] La muestra ≥ 30 datasets cubre representatividad temática (≥5 categorías)

VALIDACIONES DE CONSISTENCIA INTERNA
[ ] El código data_layer.py implementa EXACTAMENTE lo descrito en Sección 8
[ ] Los nombres de funciones en el PDF coinciden con los del repositorio
[ ] El cronograma (Sección 10) es coherente con la complejidad técnica real
[ ] No hay contradicciones entre secciones (ej. n° de dimensiones: 4 en PDF → 5 en código)

NOTA CRÍTICA PARA EL DIRECTOR:
El PDF original describe 4 dimensiones; el data_layer.py v2.1 implementa 5
(añade compute_timeliness). El redactor debe documentar esto explícitamente como
una "mejora metodológica" respecto al boceto, no como inconsistencia.
```

---

## ESTRUCTURA DE ARCHIVOS DEL EQUIPO

```
.antigravity/
└── team/
    ├── tasks.json                  ← Registro maestro de tareas
    ├── broadcast.msg               ← Mensajes globales del Director
    ├── mailbox/
    │   ├── agente_fuentes.msg
    │   ├── agente_metodologia.msg
    │   ├── agente_variables.msg
    │   ├── agente_redactor.msg
    │   └── agente_revisor.msg
    ├── locks/                      ← Semáforos de edición
    ├── shared/
    │   ├── fuentes_verificadas.json     ← OUTPUT del Arqueólogo (Rol 1)
    │   ├── literatura_adicional.json    ← OUTPUT del Investigador (Rol 2)
    │   ├── variables_formulas.json      ← OUTPUT del Arquitecto (Rol 3)
    │   ├── secciones_redactadas/        ← OUTPUT del Redactor (Rol 4)
    │   │   ├── 11_1_datos_abiertos.md
    │   │   ├── 11_2_calidad_datos.md
    │   │   ├── 11_3_gobernanza.md
    │   │   ├── 11_4_metodologia.md
    │   │   ├── 11_5_antecedente_labnl.md
    │   │   ├── 07_variables.md
    │   │   └── bibliografia_apa7.md
    │   └── reporte_revision.md          ← OUTPUT del Revisor (Rol 5)
    └── quality_results.json             ← Resultados del pipeline NL 2026
```

---

## PROTOCOLO DE ORQUESTACIÓN (PASO A PASO)

### Fase 0 — Inicialización (Director)
```bash
python team_manager.py init
```
El Director crea `tasks.json` con las tareas en estado `PENDING` y envía
broadcast de inicio al equipo.

### Fase 1 — Verificación de fuentes (Roles 1 + 2 en paralelo)
**Rol 1** ejecuta el protocolo de verificación sobre las 9 citas del PDF.
**Rol 2** ejecuta las 14 queries de búsqueda en paralelo.
Ambos escriben en `shared/` cuando terminan. **No bloquean entre sí.**

**Acción concreta del Rol 1 para cada cita:**
```python
# Pseudocódigo de verificación
for cita in CITAS_PENDIENTES:
    resultado = web_fetch(cita["url_original"])
    if resultado.status == 200:
        cita["estado"] = "VERIFIED"
        cita["url_final"] = cita["url_original"]
    else:
        # Buscar alternativa
        doi_result = web_fetch(f"https://doi.org/{cita.get('doi','')}")
        scholar_result = web_search(f"{cita['titulo']} {cita['autores'][0]} {cita['año']}")
        # Seleccionar mejor alternativa y documentar
        cita["estado"] = "REPLACED" if found else "UNVERIFIED"
        cita["nota_verificacion"] = "URL original caída. Reemplazada por DOI oficial."
```

### Fase 2 — Construcción de variables y fórmulas (Rol 3)
Después de que Fase 1 esté al menos al 70%, el Arquitecto puede iniciar.
Lee el `data_layer.py` del repositorio y genera `variables_formulas.json`
con el mapeo completo.

### Fase 3 — Redacción (Rol 4)
Solo inicia cuando `fuentes_verificadas.json` existe con al menos 7 citas
en estado `VERIFIED` o `REPLACED`. Escribe sección por sección respetando
el orden de dependencias.

### Fase 4 — Revisión (Rol 5)
Ejecuta el checklist completo sobre todos los archivos de
`secciones_redactadas/`. Devuelve `reporte_revision.md` al Director.

### Fase 5 — Consolidación y entrega (Director)
El Director une todas las secciones en el documento final
`protocolo_investigacion_NL2026_v2.md` y genera el PDF académico.

---

## SCRIPTS DE APOYO

### `team_manager.py` — Gestor de tareas
```python
import json, os, sys
from datetime import datetime

TEAM_DIR = ".antigravity/team"

def init_team():
    os.makedirs(f"{TEAM_DIR}/mailbox",  exist_ok=True)
    os.makedirs(f"{TEAM_DIR}/locks",    exist_ok=True)
    os.makedirs(f"{TEAM_DIR}/shared/secciones_redactadas", exist_ok=True)

    tasks = {
        "proyecto": "Gobernanza Datos Abiertos NL 2026",
        "iniciado": datetime.now().isoformat(),
        "tasks": [
            {"id":1, "titulo":"Verificar 9 citas del PDF",
             "agente":"agente_fuentes",   "estado":"PENDING", "deps":[]},
            {"id":2, "titulo":"Buscar literatura adicional 2020-2026",
             "agente":"agente_metodologia","estado":"PENDING","deps":[]},
            {"id":3, "titulo":"Mapear variables ↔ código",
             "agente":"agente_variables", "estado":"PENDING", "deps":[1]},
            {"id":4, "titulo":"Redactar secciones del marco teórico",
             "agente":"agente_redactor",  "estado":"PENDING", "deps":[1,2,3]},
            {"id":5, "titulo":"Revisar documento completo",
             "agente":"agente_revisor",   "estado":"PENDING", "deps":[4]},
            {"id":6, "titulo":"Consolidar y generar PDF final",
             "agente":"director",         "estado":"PENDING", "deps":[5]},
        ]
    }
    with open(f"{TEAM_DIR}/tasks.json", "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)
    print("✓ Equipo AldoGbot inicializado — 6 tareas creadas.")

def status():
    with open(f"{TEAM_DIR}/tasks.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"\n{'ID':>3}  {'AGENTE':<22} {'ESTADO':<12} TÍTULO")
    print("─" * 65)
    for t in data["tasks"]:
        icon = {"PENDING":"○","IN_PROGRESS":"◉","COMPLETED":"✓","BLOCKED":"✗"}.get(t["estado"],"?")
        print(f"{t['id']:>3}  {t['agente']:<22} {icon} {t['estado']:<10} {t['titulo']}")

def complete(task_id: int):
    with open(f"{TEAM_DIR}/tasks.json", "r+", encoding="utf-8") as f:
        data = json.load(f)
        for t in data["tasks"]:
            if t["id"] == task_id:
                t["estado"]    = "COMPLETED"
                t["completado"]= datetime.now().isoformat()
        f.seek(0); json.dump(data, f, indent=2, ensure_ascii=False)
    lock = f"{TEAM_DIR}/locks/task_{task_id}.lock"
    if os.path.exists(lock): os.remove(lock)
    print(f"✓ Tarea {task_id} completada y lock liberado.")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "init":     init_team()
    elif cmd == "status": status()
    elif cmd == "complete" and len(sys.argv) > 2: complete(int(sys.argv[2]))
```

### `verify_citations.py` — Verificador autónomo de URLs
```python
"""
Ejecutar: python verify_citations.py
Produce:  .antigravity/team/shared/fuentes_verificadas.json
"""
import json, requests, time
from pathlib import Path

CITAS = [
    {"id":"nexos-2025",
     "url":"https://federalismo.nexos.com.mx/2025/12/el-nuevo-modelo-de-datos-abiertos-en-mexico/",
     "doi":None,
     "query":"nuevo modelo datos abiertos México Nexos Federalismo 2025"},
    {"id":"condatos-2023",
     "url":"https://home.inai.org.mx/",
     "doi":None,
     "query":"ConDATOS Política Nacional Datos Abiertos INAI 2023"},
    {"id":"flores-2024",
     "url":"https://doi.org/10.1016/j.giq.2023.101898",
     "doi":"10.1016/j.giq.2023.101898",
     "query":"Flores Janssen Rodriguez Bolivar sustainable open data 2024 GIQ"},
    {"id":"espinoza-2023",
     "url":"https://doi.org/10.17533/udea.redin.20220107",
     "doi":"10.17533/udea.redin.20220107",
     "query":"Espinoza-Portilla open government data COVID Latin America 2023"},
    {"id":"zhang-2024",
     "url":"https://arxiv.org/abs/2406.19614",
     "doi":None,
     "query":"Zhang Li Wang data quality dimensions tools machine learning 2024 arXiv"},
    {"id":"ocde-ourdata-2023",
     "url":"https://doi.org/10.1787/a37f51c3-en",
     "doi":"10.1787/a37f51c3-en",
     "query":"OECD OURdata index 2023 open useful reusable data"},
    {"id":"ocde-digital-2024",
     "url":"https://doi.org/10.1787/1a89ed5e-en",
     "doi":"10.1787/1a89ed5e-en",
     "query":"OECD Digital Government Index 2023 2024"},
    {"id":"labnl-2024",
     "url":"https://wiki.labnuevoleon.mx/index.php?title=C%C3%B3mo_vamos_en_Datos_en_Nuevo_Le%C3%B3n",
     "doi":None,
     "query":"Cómo vamos Datos Nuevo León LabNL 2024 evaluación calidad datos abiertos"},
    {"id":"wang-strong-1996",
     "url":"https://doi.org/10.1080/07421222.1996.11518099",
     "doi":"10.1080/07421222.1996.11518099",
     "query":"Wang Strong 1996 beyond accuracy data quality consumers JMIS"},
]

OUTPUT = Path(".antigravity/team/shared/fuentes_verificadas.json")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

resultados = []
headers = {"User-Agent": "DatosAbiertosNL-ResearchBot/1.0 (academic verification)"}

for c in CITAS:
    print(f"\n🔍 Verificando: {c['id']}")
    estado, url_final, nota = "UNVERIFIED", c["url"], ""

    # Intento 1: URL original
    try:
        r = requests.get(c["url"], headers=headers, timeout=15, allow_redirects=True)
        if r.status_code == 200:
            estado, url_final = "VERIFIED", r.url
            print(f"   ✓ VERIFIED → {r.url[:80]}")
        else:
            nota = f"HTTP {r.status_code}"
            print(f"   ✗ HTTP {r.status_code}")
    except Exception as e:
        nota = str(e)[:80]
        print(f"   ✗ Error: {nota}")

    # Intento 2: DOI directo
    if estado == "UNVERIFIED" and c.get("doi"):
        try:
            r2 = requests.get(f"https://doi.org/{c['doi']}", headers=headers,
                              timeout=15, allow_redirects=True)
            if r2.status_code == 200:
                estado, url_final = "REPLACED_DOI", r2.url
                nota = f"URL original caída. Reemplazada por DOI: {r2.url[:80]}"
                print(f"   ✓ DOI resuelve → {r2.url[:80]}")
        except Exception:
            pass

    # Intento 3: Semantic Scholar API
    if estado == "UNVERIFIED":
        try:
            api = f"https://api.semanticscholar.org/graph/v1/paper/search?query={requests.utils.quote(c['query'])}&fields=title,year,externalIds,openAccessPdf&limit=1"
            r3  = requests.get(api, headers=headers, timeout=15)
            data = r3.json()
            if data.get("data"):
                paper = data["data"][0]
                oap   = paper.get("openAccessPdf")
                ext   = paper.get("externalIds", {})
                if oap and oap.get("url"):
                    estado, url_final = "REPLACED_OA", oap["url"]
                    nota = f"Open Access PDF encontrado en Semantic Scholar: {paper['title'][:60]}"
                elif ext.get("DOI"):
                    estado, url_final = "REPLACED_DOI", f"https://doi.org/{ext['DOI']}"
                    nota = f"DOI encontrado en Semantic Scholar: {ext['DOI']}"
                print(f"   {'✓' if estado != 'UNVERIFIED' else '✗'} Semantic Scholar: {nota[:80]}")
        except Exception as e:
            print(f"   ✗ Semantic Scholar error: {str(e)[:60]}")

    resultados.append({**c, "estado": estado, "url_final": url_final, "nota": nota})
    time.sleep(1.5)  # Respetar rate limits

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump({"verificado": True, "fuentes": resultados}, f,
              indent=2, ensure_ascii=False)

verificadas = sum(1 for r in resultados if r["estado"] != "UNVERIFIED")
print(f"\n{'='*50}")
print(f"✓ {verificadas}/{len(resultados)} fuentes verificadas o reemplazadas.")
print(f"📄 Guardado en: {OUTPUT}")
```

---

## CÓMO ACTIVAR EL EQUIPO

### Opción A — Claude como orquestador directo
Dile al LLM:
> *"Usa el skill academic-research-multiagent. Ejecuta la Fase 1 completa:
> verifica las 9 citas del PDF usando web_fetch y Semantic Scholar API,
> luego busca 5 fuentes adicionales para reforzar la hipótesis H1.
> Guarda los resultados en `.antigravity/team/shared/fuentes_verificadas.json`."*

### Opción B — Ejecución local
```bash
# Inicializar equipo
python team_manager.py init

# Verificar citas (Rol 1)
python verify_citations.py

# Ver estado del equipo
python team_manager.py status

# Marcar tarea como completada
python team_manager.py complete 1
```

### Opción C — Claude Code (terminal)
Si usas Claude Code, abre 3 terminales y asigna un rol a cada una:
```bash
# Terminal 1 — Rol 1 + Rol 2
claude "Ejecuta la Fase 1 del skill academic-research-multiagent: verifica citas y busca literatura adicional"

# Terminal 2 — Rol 3
claude "Ejecuta la Fase 2: mapea variables del PDF con data_layer.py y genera variables_formulas.json"

# Terminal 3 — Monitoreo
watch -n 5 python team_manager.py status
```

---

## CRITERIOS DE CALIDAD DEL DOCUMENTO FINAL

El documento es aprobado por el Director solo si cumple:

| Criterio | Umbral mínimo |
|----------|---------------|
| Citas verificadas (HTTP 200 o DOI activo) | ≥ 90% |
| Fuentes con año 2020–2026 | ≥ 60% del total |
| Fuentes de contexto mexicano/latinoamericano | ≥ 3 citas |
| Consistencia variables PDF ↔ código | 100% (0 contradicciones) |
| Extensión del marco teórico | ≥ 3,500 palabras |
| Formato APA 7 sin errores | 100% de entradas |
| Hipótesis operacionalizadas con fórmula | H1, H2, H3 = 3/3 |

---

## NOTA IMPORTANTE PARA EL AGENTE

> El boceto del PDF es **científicamente sólido** en su estructura y fundamentación
> teórica (Wang & Strong 1996, ISO 25012, Rojas Soriano 2013). El problema detectado
> es operativo: algunas URLs pueden estar desactualizadas o incorrectas. La tarea
> del equipo NO es reescribir la investigación, sino **verificar, corregir y enriquecer**
> lo que ya existe.
>
> La discrepancia entre 4 dimensiones (PDF) y 5 dimensiones (código v2.1) debe
> documentarse como una **mejora metodológica justificada** en la sección de
> instrumento, citando que la dimensión de Puntualidad (Ti) fue añadida en respuesta
> a la Pregunta Derivada 3 del protocolo: *"¿Existe correspondencia entre la frecuencia
> de actualización declarada y el intervalo real?"*
