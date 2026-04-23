# Data Contracts Gap — Schemas Pydantic propuestos

**Estado actual:** Pydantic v2 disponible en [requirements.txt:18](../../../requirements.txt#L18), pero sin schemas formales. El pipeline usa `dataclass` + `Enum` en [pipeline/evaluator_v1.py](../../../pipeline/evaluator_v1.py). `data_layer.py` valida manualmente con `_REQUIRED_COLS` ([data_layer.py:66-71](../../../data_layer.py#L66-L71)).

**Objetivo:** Proponer schemas Pydantic como contrato de frontera entre pipeline → storage → dashboard. **Diseño, no implementación** — la migración entra en Fase 2.

---

## 1 · `QualityReport` (salida principal de `data_layer.load_results`)

Equivalente Pydantic del dict producido por `compute_quality_scores()`.

```python
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class FrecuenciaUpdate(str, Enum):
    DIARIA = "diaria"
    SEMANAL = "semanal"
    QUINCENAL = "quincenal"
    MENSUAL = "mensual"
    TRIMESTRAL = "trimestral"
    SEMESTRAL = "semestral"
    ANUAL = "anual"
    DESCONOCIDA = "desconocida"


class QualityReport(BaseModel):
    """Resultado de calidad para un dataset. 7 dimensiones ISO 25012 + catálogo."""
    # Identificación
    dataset: str = Field(..., min_length=1)
    slug: str
    recurso_id: str
    categoria: str
    organizacion: str

    # Metadata física
    filas: int = Field(..., ge=0)
    columnas: int = Field(..., ge=0)
    modificado: Optional[datetime] = None
    frecuencia_update: FrecuenciaUpdate = FrecuenciaUpdate.DESCONOCIDA

    # Dimensiones (0-100)
    comp_completitud_global_pct: float = Field(..., ge=0, le=100)
    acc_score_accuracy_pct:      float = Field(..., ge=0, le=100)
    cons_score_consistency_pct:  float = Field(..., ge=0, le=100)
    uniq_score_uniqueness_pct:   float = Field(..., ge=0, le=100)
    time_score_timeliness_pct:   Optional[float] = Field(None, ge=0, le=100)
    doc_score_documentation_pct: float = Field(..., ge=0, le=100)
    open_score_openness_pct:     float = Field(..., ge=0, le=100)

    # Score global ponderado
    score_global: float = Field(..., ge=0, le=100)

    @field_validator("modificado", mode="before")
    @classmethod
    def parse_iso_z(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v


class QualityReportBatch(BaseModel):
    """Batch de reportes — formato de `resultados_calidad_datos_nl.csv`/.json."""
    generado: datetime
    run_id: str
    pipeline_version: str
    dimensiones: list[str]
    datasets: list[QualityReport]
```

**Uso propuesto:**
```python
# En data_layer._load_raw
batch = QualityReportBatch.model_validate_json(path_json.read_text())
df = pd.DataFrame([r.model_dump() for r in batch.datasets])
```

**Reemplaza:** `_validate_schema` ([data_layer.py:756-762](../../../data_layer.py#L756-L762)) y el parse manual de fechas.

---

## 2 · `DatasetEntry` (salida de `fetch_portal_catalog`)

Captura el descubrimiento CKAN (un recurso = una entrada).

```python
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


class FormatoRecurso(str, Enum):
    CSV = "CSV"
    JSON = "JSON"
    GEOJSON = "GEOJSON"
    XML = "XML"
    RDF = "RDF"
    SPARQL = "SPARQL"
    TSV = "TSV"
    XLS = "XLS"
    XLSX = "XLSX"
    ODS = "ODS"
    PDF = "PDF"
    OTRO = "OTRO"


class DatasetEntry(BaseModel):
    """Entrada del catálogo CKAN — un recurso evaluable."""
    slug: str
    recurso_id: str
    dataset: str
    organizacion: str = "Desconocida"
    categoria: str = "Sin categoría"
    formato: FormatoRecurso
    url: HttpUrl
    modificado: Optional[datetime] = None
    frecuencia_update: Optional[str] = None

    # Metadata documental
    descripcion: str = ""
    licencia: str = ""
    licencia_id: str = ""

    # Agregados de todos los recursos del dataset padre
    num_resources: int = Field(..., ge=0)
    resource_formats: list[str] = Field(default_factory=list)
    resource_descs: list[str] = Field(default_factory=list)
```

**Reemplaza:** el dict literal en [data_layer.py:107-126](../../../data_layer.py#L107-L126).

---

## 3 · `AnomalySignal` (salida de `pipeline/anomaly_detector.py`)

El detector actual reporta 3 tipos de anomalía.

```python
from enum import Enum
from pydantic import BaseModel, Field


class TipoAnomalia(str, Enum):
    LOW_GLOBAL_SCORE    = "low_global_score"       # score_global < 50
    CRITICAL_DIMENSION  = "critical_dimension"     # cualquier dim < 30
    CATEGORY_MISMATCH   = "category_mismatch"      # score_dim difiere >20% del mean del category


class Severidad(str, Enum):
    CRITICA = "critica"
    ALTA    = "alta"
    MEDIA   = "media"
    BAJA    = "baja"


class AnomalySignal(BaseModel):
    """Señal generada por el detector de anomalías."""
    dataset_slug: str
    tipo: TipoAnomalia
    severidad: Severidad
    dimension: Optional[str] = None     # completeness, accuracy, …
    valor_observado: float
    valor_esperado: Optional[float] = None
    delta_pct: Optional[float] = None   # solo para CATEGORY_MISMATCH
    mensaje: str
    generado: datetime
```

---

## 4 · `RefreshTask` (contrato de `pipeline/refresh_engine.py`)

```python
from pydantic import BaseModel


class RefreshTask(BaseModel):
    """Tarea de refresco ejecutable por refresh_engine."""
    dataset_slug: str
    recurso_id: str
    url: HttpUrl
    formato: FormatoRecurso
    ttl_hours: int = Field(24, ge=1, le=720)
    force: bool = False


class RefreshResult(BaseModel):
    task: RefreshTask
    success: bool
    started_at: datetime
    finished_at: datetime
    duration_seconds: float
    error: Optional[str] = None
    report: Optional[QualityReport] = None
```

---

## 5 · `DiccionarioDato` (NUEVO — no existe hoy)

Propuesta: cada dataset debería tener un diccionario de datos versionado.

```python
from pydantic import BaseModel


class ColumnSpec(BaseModel):
    nombre: str
    tipo: str                    # int, float, str, date, bool
    obligatoria: bool = False
    descripcion: str = ""
    regex: Optional[str] = None
    dominio: Optional[list[str]] = None  # valores permitidos
    rango_min: Optional[float] = None
    rango_max: Optional[float] = None


class DiccionarioDato(BaseModel):
    """Contrato formal del schema de un dataset."""
    dataset_slug: str
    version: str
    columnas: list[ColumnSpec]
    natural_key: list[str] = Field(default_factory=list)  # unicidad compuesta
    frecuencia_esperada: FrecuenciaUpdate
```

**Beneficio:** habilita las expectations explícitas de Great Expectations ([pipeline_audit.md](pipeline_audit.md)) y convierte el pipeline de "descriptivo" a "contract-based".

**Ubicación propuesta Fase 2:** `pipeline/contracts/<slug>.yaml` con serialización Pydantic ↔ YAML.

---

## 6 · Gaps de adopción

### Problemas a resolver en Fase 2

1. **Dónde viven los schemas** — no existe `pipeline/schemas.py` ni `models.py`. Proponer `pipeline/contracts/__init__.py` como módulo dedicado.
2. **Serialización CSV ↔ Pydantic** — el CSV actual pierde tipos (fechas como string, Enums como string crudo). Usar `model_validate` + `.model_dump()` explícitamente.
3. **Migración sin ruptura** — `_load_raw` debería:
   - a) Intentar deserializar con Pydantic.
   - b) Si falla, fallback al parse actual + log warning.
   - c) En Fase 3, exigir validación estricta.
4. **Testing de contratos** — pytest fixtures con `QualityReport.model_validate(...)` sobre samples reales del pipeline.

### Riesgos

- **Overhead:** Pydantic v2 es rápido, pero 272 datasets × ~20 campos cada uno (~5400 validaciones por refresh). Medir antes de asumir problema.
- **Versionado:** Si cambia el schema (nueva dimensión), todos los reportes viejos se invalidan. Mitigar con campo `schema_version` en `QualityReportBatch`.

---

## Check de alineamiento con pipeline actual

| Campo usado en UI | Presente en `QualityReport` | Origen actual |
|---|---|---|
| `dataset`, `categoria`, `organizacion` | ✅ | CSV/JSON |
| `filas`, `columnas` | ✅ | CSV/JSON |
| `score_global` | ✅ | Calculado pipeline |
| 7 dimensiones pct | ✅ | Pipeline |
| `modificado` | ✅ | CKAN metadata |
| `frecuencia_update` | ✅ | CKAN metadata |
| `slug` (para URL CKAN) | ✅ | Pipeline (a veces ausente en CSV) |
| `recurso_id` | ✅ | Pipeline |

**Columnas del CSV actual NO modeladas aún:** `descripcion_ciudadana`, `tags_sugeridos` — son enrichment opcional ([pipeline/ai_enrichment.py](../../../pipeline/ai_enrichment.py)). Añadir como `Optional[...]` en `QualityReport` cuando se estabilice su generación.
