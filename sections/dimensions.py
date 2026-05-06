"""Single source of truth for ISO/IEC 25012 dimension metadata.

All section modules import from here instead of redefining the 7-dimension
structure. DIM_LABEL_MAP in data_layer.py is the canonical col→label map;
this module re-exports it and derives the convenience structures used across
sections.
"""
from data_layer import DIM_LABEL_MAP

# Ordered list of (column_name, display_label) for all 7 dims (excl. score_global)
DIM_COLS: list[tuple[str, str]] = [
    (col, label)
    for col, label in DIM_LABEL_MAP.items()
    if col != "score_global"
]

# Citizen-facing labels + descriptions for health bars (metodologia, conclusiones)
# Each value is (display_label, plain-language description)
CITIZEN_LABELS: dict[str, tuple[str, str]] = {
    "Completitud"   : ("Datos Completos",    "¿Los registros están completos?"),
    "Exactitud"     : ("Información Exacta", "¿Los valores son correctos y verificables?"),
    "Consistencia"  : ("Datos Congruentes",  "¿Los datos no se contradicen entre sí?"),
    "Unicidad"      : ("Sin Duplicados",     "¿Cada registro aparece una sola vez?"),
    "Puntualidad"   : ("Datos Actuales",     "¿La información está al día?"),
    "Documentación" : ("Bien Documentado",   "¿El dataset tiene metadatos descriptivos?"),
    "Apertura"      : ("Datos Abiertos",     "¿El formato es reutilizable y libre?"),
}
