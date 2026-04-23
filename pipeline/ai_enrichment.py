"""
ai_enrichment.py
Módulo para enriquecer metadatos de conjuntos de datos con Vertex AI (Gemini Flash).
Convierte metadatos técnicos en lenguaje accesible para ciudadanos.
"""
import json
import logging
import vertexai
from vertexai.generative_models import GenerativeModel
import os
import time

logger = logging.getLogger(__name__)

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "datos-abiertos-nl")
LOCATION = os.getenv("GCP_LOCATION", "us-central1")
MODEL_ID = "gemini-1.5-flash-001"

_is_vertex_initialized = False
_MAX_CONSECUTIVE_FAILURES = 3  # Abort AI enrichment after N consecutive auth/quota errors


def init_vertex() -> bool:
    global _is_vertex_initialized
    if _is_vertex_initialized:
        return True
    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        _is_vertex_initialized = True
        return True
    except Exception as e:
        logger.error(f"Fallo al inicializar Vertex AI: {e}", exc_info=True)
        return False


def enrich_dataset_metadata(dataset_records: list[dict]) -> list[dict]:
    """
    Toma una lista de registros (dictionaries) y usa Gemini 1.5 Flash
    para añadir `descripcion_ciudadana` y `tags_sugeridos`.
    Aborta silenciosamente si las credenciales no están disponibles.
    """
    if not init_vertex():
        logger.warning("Vertex AI no inicializado. Se retorna la data sin enriquecer.")
        return dataset_records

    model = GenerativeModel(MODEL_ID)
    consecutive_failures = 0

    for row in dataset_records:
        titulo = row.get("dataset", "")
        desc = row.get("descripcion", "")
        org = row.get("organizacion", "")

        # Saltamos si no hay título o si ya fue enriquecido
        if not titulo or "descripcion_ciudadana" in row:
            row.setdefault("descripcion_ciudadana", "")
            row.setdefault("tags_sugeridos", [])
            continue

        prompt = f"""
        Eres un traductor experto en lenguaje ciudadano. El gobierno de Nuevo León publica este dataset de datos abiertos:

        Organización: {org}
        Título: {titulo}
        Descripción técnica: {desc}

        Proporciona un JSON con 2 campos:
        1. "descripcion_ciudadana": Una o dos oraciones amigables que expliquen a un ciudadano común (sin jerga) qué es esto y para qué le sirve.
        2. "tags_sugeridos": Arreglo de 3 a 5 palabras clave breves para búsqueda y categorización.

        Responde ÚNICAMENTE con el objeto JSON válido. Sin markdown ticks.
        """

        try:
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.2, "response_mime_type": "application/json"},
            )
            ai_data = json.loads(response.text)
            row["descripcion_ciudadana"] = ai_data.get("descripcion_ciudadana", "")
            row["tags_sugeridos"] = ai_data.get("tags_sugeridos", [])
            consecutive_failures = 0
            time.sleep(1)  # Respetar rate limits solo en éxito
        except Exception as e:
            logger.warning(f"Error AI para '{titulo}': {e}")
            row["descripcion_ciudadana"] = ""
            row["tags_sugeridos"] = []
            consecutive_failures += 1
            if consecutive_failures >= _MAX_CONSECUTIVE_FAILURES:
                logger.warning(
                    "AI enrichment abortado tras %d fallos consecutivos. "
                    "Verifique las credenciales de Vertex AI.",
                    consecutive_failures,
                )
                # Rellenar campos vacíos para el resto de los registros
                for remaining in dataset_records:
                    remaining.setdefault("descripcion_ciudadana", "")
                    remaining.setdefault("tags_sugeridos", [])
                break

    return dataset_records
