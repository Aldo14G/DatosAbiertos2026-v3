"""
SKILL 2: Evaluador de Calidad de Datos - Full Stack Data Analyst
=================================================================
Evaluación basada en ISO 25012, ISO 8000 y DAMA-DMBOK 2.0
Optimizado para datos gubernamentales de Nuevo León, México.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import Counter
import re
import json
import hashlib
import logging
import os

# Intento de importar Vertex AI para análisis semántico
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    _AI_AVAILABLE = True
except ImportError:
    _AI_AVAILABLE = False

# ============================================================
# MODELOS Y ENUMERACIONES
# ============================================================

class SeveridadProblema(Enum):
    CRITICA = "critica"
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"
    INFORMATIVA = "informativa"

class CategoriaProblema(Enum):
    COMPLETITUD = "completitud"
    EXACTITUD = "exactitud"
    CONSISTENCIA = "consistencia"
    ACTUALIDAD = "actualidad"
    UNICIDAD = "unicidad"
    CONFORMIDAD = "conformidad"
    INTEGRIDAD_REFERENCIAL = "integridad_referencial"
    ACCESIBILIDAD = "accesibilidad"
    TRAZABILIDAD = "trazabilidad"
    COMPRENSIBILIDAD = "comprensibilidad"
    SEMANTICA = "exactitud_semantica"

class MarcoReferencia(Enum):
    ISO_25012 = "ISO/IEC 25012"
    ISO_8000 = "ISO 8000"
    DAMA_DMBOK = "DAMA-DMBOK"
    IA_GENERATIVA = "Análisis Semántico IA"

class NivelAnalisis(Enum):
    RAPIDO = "rapido"
    ESTANDAR = "estandar"
    PROFUNDO = "profundo"

@dataclass
class ProblemaDetectado:
    problema_id: str
    dataset_id: str
    recurso_id: str
    categoria: CategoriaProblema
    severidad: SeveridadProblema
    marco_referencia: MarcoReferencia
    titulo: str
    descripcion: str
    columnas_afectadas: List[str] = field(default_factory=list)
    registros_affected: int = 0 # Corregido de registros_afectados para consistencia si es necesario, pero mantengamos el original
    registros_afectados: int = 0
    porcentaje_afectado: float = 0.0
    ejemplo_valores: List[Any] = field(default_factory=list)
    recomendacion: str = ""
    metrica_asociada: Optional[str] = None
    valor_metrica: Optional[float] = None

@dataclass
class MetricaCalidad:
    nombre: str
    categoria: CategoriaProblema
    marco_referencia: MarcoReferencia
    valor: float
    umbral_aceptable: float
    aprobado: bool
    detalles: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ReporteDataset:
    dataset_id: str
    recurso_id: str
    titulo: str
    organizacion: str
    score_global: float = 0.0
    score_iso_25012: float = 0.0
    score_iso_8000: float = 0.0
    score_dama: float = 0.0
    score_ia_semantica: Optional[float] = None
    metricas: List[MetricaCalidad] = field(default_factory=list)
    problemas: List[ProblemaDetectado] = field(default_factory=list)
    estadisticas_basicas: Dict[str, Any] = field(default_factory=dict)
    clasificacion: str = ""

@dataclass
class ReporteGlobal:
    timestamp_evaluacion: str
    url_catalogo: str
    total_datasets_evaluados: int = 0
    total_problemas_detectados: int = 0
    score_promedio_catalogo: float = 0.0
    distribucion_clasificacion: Dict[str, int] = field(default_factory=dict)
    problemas_por_severidad: Dict[str, int] = field(default_factory=dict)
    problemas_por_categoria: Dict[str, int] = field(default_factory=dict)
    promedio_por_organizacion: Dict[str, float] = field(default_factory=dict)
    top_problemas_recurrentes: List[Dict] = field(default_factory=list)
    reportes_datasets: List[ReporteDataset] = field(default_factory=list)
    recomendaciones_priorizadas: List[Dict] = field(default_factory=list)
    resumen_ejecutivo: str = ""

# ============================================================
# ANALIZADORES POR MARCO DE REFERENCIA
# ============================================================

class AnalizadorSemanticoIA:
    """Detecta discrepancias entre la descripción técnica y los datos reales usando IA."""
    
    def __init__(self, project_id: str = None, location: str = "us-central1"):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT", "datos-abiertos-nl")
        self.location = location
        self.initialized = False
        self.logger = logging.getLogger("AnalizadorSemanticoIA")
        
    def _init_ai(self) -> bool:
        if not _AI_AVAILABLE: return False
        if self.initialized: return True
        try:
            vertexai.init(project=self.project_id, location=self.location)
            self.model = GenerativeModel("gemini-1.5-flash-001")
            self.initialized = True
            return True
        except Exception as e:
            self.logger.warning(f"No se pudo inicializar Vertex AI: {e}")
            return False

    def analizar_discrepancia(
        self, df: pd.DataFrame, metadata: Dict
    ) -> Tuple[Optional[MetricaCalidad], List[ProblemaDetectado]]:
        if not self._init_ai():
            return None, []

        titulo = metadata.get("titulo_dataset", "")
        descripcion_ckan = metadata.get("descripcion", "") or metadata.get("notes", "")
        columnas = df.columns.tolist()
        muestra = df.head(5).to_json(orient="records")
        
        prompt = f"""
        Actúa como un Auditor de Calidad de Datos. Evalúa si existe una discrepancia entre lo que dice la descripción de un dataset y lo que realmente contienen sus datos.

        METADATOS:
        Título: {titulo}
        Descripción declarada: {descripcion_ckan}

        DATOS REALES:
        Columnas: {columnas}
        Muestra de datos (primeras 5 filas): {muestra}

        TAREAS:
        1. Identifica si la descripción coincide con las columnas y datos reales.
        2. Detecta si faltan columnas mencionadas en la descripción.
        3. Detecta si los datos no corresponden al tema declarado (ej: dice ser de salud pero contiene finanzas).
        4. Asigna un score de "Exactitud Semántica" de 0 a 100.

        RESPUESTA:
        Responde ÚNICAMENTE con un objeto JSON válido con este formato:
        {{
            "score_semantico": float,
            "discrepancia_detectada": bool,
            "motivo": "string",
            "hallazgos": ["list of strings"],
            "recomendacion": "string",
            "severidad": "baja|media|alta|critica"
        }}
        """

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"temperature": 0.1, "response_mime_type": "application/json"}
            )
            res = json.loads(response.text)
            
            score = res.get("score_semantico", 100.0)
            problemas = []
            
            metrica = MetricaCalidad(
                nombre="exactitud_semantica",
                categoria=CategoriaProblema.SEMANTICA,
                marco_referencia=MarcoReferencia.IA_GENERATIVA,
                valor=score,
                umbral_aceptable=80.0,
                aprobado=score >= 80.0,
                detalles=res
            )
            
            if res.get("discrepancia_detectada"):
                sev_map = {
                    "baja": SeveridadProblema.BAJA,
                    "media": SeveridadProblema.MEDIA,
                    "alta": SeveridadProblema.ALTA,
                    "critica": SeveridadProblema.CRITICA
                }
                problemas.append(ProblemaDetectado(
                    problema_id=hashlib.md5(f"semantica_{metadata.get('dataset_id')}".encode()).hexdigest()[:12],
                    dataset_id=metadata.get("dataset_id", ""),
                    recurso_id=metadata.get("recurso_id", ""),
                    categoria=CategoriaProblema.SEMANTICA,
                    severidad=sev_map.get(res.get("severidad", "media"), SeveridadProblema.MEDIA),
                    marco_referencia=MarcoReferencia.IA_GENERATIVA,
                    titulo="Discrepancia Semántica Detectada",
                    descripcion=res.get("motivo", "La descripción no coincide con el contenido de los datos."),
                    columnas_afectadas=columnas,
                    recomendacion=res.get("recomendacion", ""),
                    metrica_asociada="score_semantico",
                    valor_metrica=score
                ))
                
            return metrica, problemas
        except Exception as e:
            self.logger.error(f"Error en análisis semántico IA: {e}")
            return None, []

class AnalizadorISO25012:
    PATRON_CURP = re.compile(r'^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$')
    PATRON_RFC = re.compile(r'^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$')
    PATRON_CP_MEXICO = re.compile(r'^\d{5}$')
    PATRON_TELEFONO_MX = re.compile(r'^(\+52|52)?[\s-]?\d{10}$')
    PATRON_EMAIL = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PATRON_FECHA_MX = re.compile(r'^\d{2}/\d{2}/\d{4}$')
    PATRON_CLAVE_MUNICIPIO_NL = re.compile(r'^19\d{3}$')

    MUNICIPIOS_NL = [
        "Abasolo", "Agualeguas", "Allende", "Anáhuac", "Apodaca",
        "Aramberri", "Bustamante", "Cadereyta Jiménez", "Cerralvo",
        "China", "Ciénega de Flores", "Doctor Arroyo", "Doctor Coss",
        "Doctor González", "El Carmen", "Galeana", "García",
        "General Bravo", "General Escobedo", "General Terán",
        "General Treviño", "General Zaragoza", "General Zuazua",
        "Guadalupe", "Hidalgo", "Higueras", "Hualahuises",
        "Iturbide", "Juárez", "Lampazos de Naranjo", "Linares",
        "Los Aldamas", "Los Herreras", "Los Ramones", "Marín",
        "Melchor Ocampo", "Mier y Noriega", "Mina", "Montemorelos",
        "Monterrey", "Parás", "Pesquería", "Rayones",
        "Sabinas Hidalgo", "Salinas Victoria", "San Nicolás de los Garza",
        "San Pedro Garza García", "Santa Catarina", "Santiago",
        "Vallecillo", "Villaldama",
    ]

    def __init__(self):
        self.logger = logging.getLogger("ISO25012")

    def analizar(
        self, df: pd.DataFrame, metadata: Dict, nivel: NivelAnalisis = NivelAnalisis.ESTANDAR
    ) -> Tuple[List[MetricaCalidad], List[ProblemaDetectado]]:
        metricas, problemas = [], []
        dataset_id = metadata.get("dataset_id", "")
        recurso_id = metadata.get("recurso_id", "")

        for evaluator in [
            self._evaluar_completitud, self._evaluar_exactitud,
            self._evaluar_consistencia, self._evaluar_conformidad,
            self._evaluar_comprensibilidad
        ]:
            m, p = evaluator(df, dataset_id, recurso_id)
            metricas.extend(m)
            problemas.extend(p)

        m, p = self._evaluar_actualidad(df, metadata, dataset_id, recurso_id)
        metricas.extend(m)
        problemas.extend(p)

        if nivel == NivelAnalisis.PROFUNDO:
            m, p = self._evaluar_precision(df, dataset_id, recurso_id)
            metricas.extend(m)
            problemas.extend(p)

        return metricas, problemas

    def _evaluar_completitud(self, df: pd.DataFrame, dataset_id: str, recurso_id: str) -> Tuple[List[MetricaCalidad], List[ProblemaDetectado]]:
        metricas, problemas = [], []
        total_celdas = df.shape[0] * df.shape[1]
        nulos_total = df.isnull().sum().sum()
        completitud_general = ((1 - nulos_total / total_celdas) * 100 if total_celdas > 0 else 0)

        metricas.append(MetricaCalidad(
            nombre="completitud_general", categoria=CategoriaProblema.COMPLETITUD,
            marco_referencia=MarcoReferencia.ISO_25012, valor=round(completitud_general, 2),
            umbral_aceptable=85.0, aprobado=completitud_general >= 85.0,
            detalles={"total_celdas": total_celdas, "celdas_nulas": int(nulos_total), "celdas_completas": total_celdas - int(nulos_total)}
        ))
        
        for col in df.columns:
            nulos_col = df[col].isnull().sum()
            pct_nulos = (nulos_col / len(df) * 100) if len(df) > 0 else 0
            if pct_nulos > 50: severidad = SeveridadProblema.ALTA
            elif pct_nulos > 20: severidad = SeveridadProblema.MEDIA
            elif pct_nulos > 5: severidad = SeveridadProblema.BAJA
            else: continue

            problemas.append(ProblemaDetectado(
                problema_id=hashlib.md5(f"completitud_{dataset_id}_{col}".encode()).hexdigest()[:12],
                dataset_id=dataset_id, recurso_id=recurso_id, categoria=CategoriaProblema.COMPLETITUD,
                severidad=severidad, marco_referencia=MarcoReferencia.ISO_25012,
                titulo=f"Valores faltantes en '{col}'",
                descripcion=f"La columna '{col}' tiene {nulos_col} valores nulos ({pct_nulos:.1f}% del total)",
                columnas_afectadas=[col], registros_afectados=int(nulos_col), porcentaje_afectado=round(pct_nulos, 2),
                recomendacion=self._recomendar_completitud(col, pct_nulos),
                metrica_asociada="completitud_columna", valor_metrica=round(100 - pct_nulos, 2)
            ))
        return metricas, problemas

    def _evaluar_exactitud(self, df: pd.DataFrame, dataset_id: str, recurso_id: str) -> Tuple[List[MetricaCalidad], List[ProblemaDetectado]]:
        metricas, problemas = [], []
        # Implementación simplificada para brevedad
        return metricas, problemas

    def _evaluar_consistencia(self, df: pd.DataFrame, dataset_id: str, recurso_id: str) -> Tuple[List[MetricaCalidad], List[ProblemaDetectado]]:
        metricas, problemas = [], []
        return metricas, problemas

    def _evaluar_actualidad(self, df: pd.DataFrame, metadata: Dict, dataset_id: str, recurso_id: str) -> Tuple[List[MetricaCalidad], List[ProblemaDetectado]]:
        metricas, problemas = [], []
        return metricas, problemas

    def _evaluar_conformidad(self, df: pd.DataFrame, dataset_id: str, recurso_id: str) -> Tuple[List[MetricaCalidad], List[ProblemaDetectado]]:
        metricas, problemas = [], []
        if df.empty or df.shape[1] == 0:
            metricas.append(MetricaCalidad(
                nombre="conformidad_general", categoria=CategoriaProblema.CONFORMIDAD,
                marco_referencia=MarcoReferencia.ISO_25012, valor=0.0,
                umbral_aceptable=75.0, aprobado=False,
                detalles={"motivo": "dataframe vacio"},
            ))
            return metricas, problemas

        detectores = [
            ("curp", self.PATRON_CURP),
            ("rfc", self.PATRON_RFC),
            ("codigo_postal", self.PATRON_CP_MEXICO),
            ("cp", self.PATRON_CP_MEXICO),
            ("telefono", self.PATRON_TELEFONO_MX),
            ("email", self.PATRON_EMAIL),
            ("correo", self.PATRON_EMAIL),
            ("fecha", self.PATRON_FECHA_MX),
            ("cve_mun", self.PATRON_CLAVE_MUNICIPIO_NL),
        ]

        tasas, cols_evaluadas = [], []
        for col in df.columns:
            col_lower = str(col).lower()
            for token, patron in detectores:
                if token in col_lower:
                    valores = df[col].dropna().astype(str).str.strip()
                    if len(valores) == 0:
                        continue
                    matches = int(valores.str.match(patron).sum())
                    tasa = matches / len(valores) * 100.0
                    tasas.append(tasa)
                    cols_evaluadas.append(col)
                    if tasa < 75.0:
                        problemas.append(ProblemaDetectado(
                            problema_id=hashlib.md5(f"conformidad_{dataset_id}_{col}".encode()).hexdigest()[:12],
                            dataset_id=dataset_id, recurso_id=recurso_id,
                            categoria=CategoriaProblema.CONFORMIDAD,
                            severidad=SeveridadProblema.MEDIA if tasa >= 50.0 else SeveridadProblema.ALTA,
                            marco_referencia=MarcoReferencia.ISO_25012,
                            titulo=f"Formato no conforme en '{col}'",
                            descripcion=f"{100 - tasa:.1f}% de valores en '{col}' no cumplen el patron esperado ({token}).",
                            columnas_afectadas=[col], registros_afectados=len(valores) - matches,
                            porcentaje_afectado=round(100 - tasa, 2),
                            recomendacion=f"Normalizar formato en '{col}' segun estandar {token.upper()}.",
                            metrica_asociada="conformidad_columna", valor_metrica=round(tasa, 2),
                        ))
                    break

        if tasas:
            score = float(np.mean(tasas))
            detalles = {"columnas_evaluadas": cols_evaluadas, "columnas_con_patron": len(tasas)}
        else:
            obj_cols = df.select_dtypes(include=["object"]).columns
            mixed = 0
            for col in obj_cols:
                sample = df[col].dropna().astype(str).head(200)
                if len(sample) == 0:
                    continue
                num_like = int(sample.str.match(r"^-?\d+(\.\d+)?$").sum())
                if 0 < num_like < len(sample) and num_like / len(sample) > 0.3:
                    mixed += 1
            total = max(len(df.columns), 1)
            score = max(0.0, 100.0 - (mixed / total) * 100.0)
            detalles = {"motivo": "sin columnas con patron detectable", "columnas_tipo_mixto": mixed}

        score = round(float(score), 2)
        metricas.append(MetricaCalidad(
            nombre="conformidad_general", categoria=CategoriaProblema.CONFORMIDAD,
            marco_referencia=MarcoReferencia.ISO_25012, valor=score,
            umbral_aceptable=75.0, aprobado=score >= 75.0, detalles=detalles,
        ))
        return metricas, problemas

    def _evaluar_comprensibilidad(self, df: pd.DataFrame, dataset_id: str, recurso_id: str) -> Tuple[List[MetricaCalidad], List[ProblemaDetectado]]:
        metricas, problemas = [], []
        total = df.shape[1]
        if total == 0:
            metricas.append(MetricaCalidad(
                nombre="comprensibilidad_general", categoria=CategoriaProblema.COMPRENSIBILIDAD,
                marco_referencia=MarcoReferencia.ISO_25012, valor=0.0,
                umbral_aceptable=70.0, aprobado=False,
                detalles={"motivo": "sin columnas"},
            ))
            return metricas, problemas

        nombres_pobres, ejemplos = 0, []
        for col in df.columns:
            nombre = str(col).strip()
            es_pobre = (
                len(nombre) < 3
                or nombre.lower().startswith("unnamed")
                or not re.search(r"[aeiouáéíóúAEIOUÁÉÍÓÚ]", nombre)
                or re.fullmatch(r"[A-Za-z]?\d+", nombre) is not None
            )
            if es_pobre:
                nombres_pobres += 1
                if len(ejemplos) < 5:
                    ejemplos.append(nombre)

        score = round(max(0.0, (1 - nombres_pobres / total) * 100.0), 2)

        if nombres_pobres > 0:
            proporcion = nombres_pobres / total
            problemas.append(ProblemaDetectado(
                problema_id=hashlib.md5(f"comprensibilidad_{dataset_id}".encode()).hexdigest()[:12],
                dataset_id=dataset_id, recurso_id=recurso_id,
                categoria=CategoriaProblema.COMPRENSIBILIDAD,
                severidad=SeveridadProblema.ALTA if proporcion >= 0.3 else SeveridadProblema.MEDIA,
                marco_referencia=MarcoReferencia.ISO_25012,
                titulo=f"{nombres_pobres} columna(s) con nombres poco comprensibles",
                descripcion=f"Ejemplos: {', '.join(ejemplos)}.",
                columnas_afectadas=ejemplos, registros_afectados=0,
                porcentaje_afectado=round(proporcion * 100.0, 2),
                recomendacion="Renombrar a snake_case descriptivo (>=3 chars, sin codigos numericos).",
            ))

        metricas.append(MetricaCalidad(
            nombre="comprensibilidad_general", categoria=CategoriaProblema.COMPRENSIBILIDAD,
            marco_referencia=MarcoReferencia.ISO_25012, valor=score,
            umbral_aceptable=70.0, aprobado=score >= 70.0,
            detalles={"nombres_pobres": nombres_pobres, "total_columnas": total, "ejemplos": ejemplos},
        ))
        return metricas, problemas

    def _evaluar_precision(self, df: pd.DataFrame, dataset_id: str, recurso_id: str) -> Tuple[List[MetricaCalidad], List[ProblemaDetectado]]:
        metricas, problemas = [], []
        return metricas, problemas

    @staticmethod
    def _recomendar_completitud(col: str, pct_nulos: float) -> str:
        if pct_nulos > 80: return f"Evaluar eliminación de columna '{col}'."
        return "Implementar proceso de captura obligatoria o valor por defecto."

class AnalizadorISO8000:
    def __init__(self):
        self.logger = logging.getLogger("ISO8000")

    def analizar(
        self, df: pd.DataFrame, metadata: Dict, todos_datasets: Dict[str, Any] = None,
    ) -> Tuple[List[MetricaCalidad], List[ProblemaDetectado]]:
        metricas, problemas = [], []
        dataset_id = metadata.get("dataset_id", "")
        recurso_id = metadata.get("recurso_id", "")
        
        m, p = self._evaluar_unicidad(df, dataset_id, recurso_id)
        metricas.extend(m); problemas.extend(p)

        m, p = self._evaluar_conformidad_sintactica(df, dataset_id, recurso_id)
        metricas.extend(m); problemas.extend(p)
        
        if todos_datasets:
            m, p = self._evaluar_integridad_referencial(df, metadata, todos_datasets, dataset_id, recurso_id)
            metricas.extend(m); problemas.extend(p)

        m, p = self._evaluar_trazabilidad(df, metadata, dataset_id, recurso_id)
        metricas.extend(m); problemas.extend(p)

        return metricas, problemas

    def _evaluar_unicidad(self, df: pd.DataFrame, dataset_id: str, recurso_id: str) -> Tuple[List[MetricaCalidad], List[ProblemaDetectado]]:
        metricas, problemas = [], []
        try:
            duplicados = df.astype(str).duplicated().sum()
        except Exception:
            duplicados = 0

        pct_dup = round((duplicados / len(df) * 100) if len(df) > 0 else 0, 2)
        metricas.append(MetricaCalidad(
            nombre="unicidad_registros", categoria=CategoriaProblema.UNICIDAD,
            marco_referencia=MarcoReferencia.ISO_8000, valor=max(0, 100 - pct_dup),
            umbral_aceptable=95.0, aprobado=pct_dup < 5
        ))
        return metricas, problemas

    def _evaluar_conformidad_sintactica(self, df: pd.DataFrame, dataset_id: str, recurso_id: str) -> Tuple[List[MetricaCalidad], List[ProblemaDetectado]]:
        metricas, problemas = [], []
        return metricas, problemas

    def _evaluar_integridad_referencial(self, df: pd.DataFrame, metadata: Dict, todos_datasets: Dict, dataset_id: str, recurso_id: str) -> Tuple[List[MetricaCalidad], List[ProblemaDetectado]]:
        metricas, problemas = [], []
        return metricas, problemas

    def _evaluar_trazabilidad(self, df: pd.DataFrame, metadata: Dict, dataset_id: str, recurso_id: str) -> Tuple[List[MetricaCalidad], List[ProblemaDetectado]]:
        metricas, problemas = [], []
        return metricas, problemas

class AnalizadorDAMA:
    def __init__(self):
        self.logger = logging.getLogger("DAMA")

    def analizar(
        self, df: pd.DataFrame, metadata: Dict, manifiesto: Dict, todos_datasets: Dict = None,
    ) -> Tuple[List[MetricaCalidad], List[ProblemaDetectado]]:
        metricas, problemas = [], []
        dataset_id = metadata.get("dataset_id", "")
        recurso_id = metadata.get("recurso_id", "")

        for evaluator in [
            self._evaluar_gobernanza, self._evaluar_metadatos
        ]:
            m, p = evaluator(metadata, dataset_id, recurso_id)
            metricas.extend(m); problemas.extend(p)
            
        for evaluator in [
            self._evaluar_arquitectura, self._evaluar_interoperabilidad
        ]:
            m, p = evaluator(df, dataset_id, recurso_id)
            metricas.extend(m); problemas.extend(p)

        return metricas, problemas

    @staticmethod
    def _meta_valor_presente(metadata: Optional[Dict], campo: str) -> bool:
        if not metadata:
            return False
        valor = metadata.get(campo)
        if valor is None:
            return False
        if isinstance(valor, str) and not valor.strip():
            return False
        if isinstance(valor, (list, tuple, dict)) and len(valor) == 0:
            return False
        return True

    def _evaluar_gobernanza(self, metadata: Dict, dataset_id: str, recurso_id: str) -> Tuple[List[MetricaCalidad], List[ProblemaDetectado]]:
        metricas, problemas = [], []
        campos = ["author", "maintainer", "maintainer_email", "license_id", "organization", "state"]
        ausentes = [c for c in campos if not self._meta_valor_presente(metadata, c)]
        presentes = len(campos) - len(ausentes)
        score = round(presentes / len(campos) * 100.0, 2)
        aprobado = score >= 75.0

        if ausentes:
            problemas.append(ProblemaDetectado(
                problema_id=hashlib.md5(f"gobernanza_{dataset_id}".encode()).hexdigest()[:12],
                dataset_id=dataset_id, recurso_id=recurso_id,
                categoria=CategoriaProblema.TRAZABILIDAD,
                severidad=SeveridadProblema.ALTA if score < 50 else SeveridadProblema.MEDIA,
                marco_referencia=MarcoReferencia.DAMA_DMBOK,
                titulo="Metadatos de gobernanza incompletos",
                descripcion=f"Faltan campos: {', '.join(ausentes)}.",
                recomendacion="Completar metadatos CKAN (author, maintainer, licencia, organizacion).",
            ))

        metricas.append(MetricaCalidad(
            "gobernanza", CategoriaProblema.TRAZABILIDAD, MarcoReferencia.DAMA_DMBOK,
            score, 75.0, aprobado,
            detalles={"campos_presentes": presentes, "campos_totales": len(campos), "ausentes": ausentes},
        ))
        return metricas, problemas

    def _evaluar_arquitectura(self, df: pd.DataFrame, dataset_id: str, recurso_id: str) -> Tuple[List[MetricaCalidad], List[ProblemaDetectado]]:
        metricas, problemas = [], []
        if df.shape[1] == 0:
            metricas.append(MetricaCalidad(
                "arquitectura_datos", CategoriaProblema.CONFORMIDAD, MarcoReferencia.DAMA_DMBOK,
                0.0, 70.0, False, detalles={"motivo": "sin columnas"},
            ))
            return metricas, problemas

        score, motivos = 100.0, []
        unnamed = [c for c in df.columns if str(c).lower().startswith("unnamed")]
        if unnamed:
            penalty = min(20.0, len(unnamed) * 5.0)
            score -= penalty
            motivos.append(f"{len(unnamed)} columna(s) sin nombre")

        id_cols = [c for c in df.columns if re.search(r"(^|_)id($|_)|^cve_|clave", str(c).lower())]
        if not id_cols:
            score -= 15.0
            motivos.append("sin columna identificadora detectable")

        try:
            dup_cols = int(df.T.duplicated().sum())
        except Exception:
            dup_cols = 0
        if dup_cols > 0:
            score -= 15.0
            motivos.append(f"{dup_cols} columna(s) con contenido duplicado")

        score = max(0.0, round(float(score), 2))
        aprobado = score >= 70.0
        if motivos:
            problemas.append(ProblemaDetectado(
                problema_id=hashlib.md5(f"arquitectura_{dataset_id}".encode()).hexdigest()[:12],
                dataset_id=dataset_id, recurso_id=recurso_id,
                categoria=CategoriaProblema.CONFORMIDAD,
                severidad=SeveridadProblema.MEDIA if aprobado else SeveridadProblema.ALTA,
                marco_referencia=MarcoReferencia.DAMA_DMBOK,
                titulo="Arquitectura de datos con debilidades",
                descripcion="; ".join(motivos),
                recomendacion="Normalizar nombres, definir identificador primario, eliminar columnas duplicadas.",
            ))
        metricas.append(MetricaCalidad(
            "arquitectura_datos", CategoriaProblema.CONFORMIDAD, MarcoReferencia.DAMA_DMBOK,
            score, 70.0, aprobado, detalles={"motivos": motivos, "columnas_sin_nombre": len(unnamed), "columnas_duplicadas": dup_cols},
        ))
        return metricas, problemas

    def _evaluar_metadatos(self, metadata: Dict, dataset_id: str, recurso_id: str) -> Tuple[List[MetricaCalidad], List[ProblemaDetectado]]:
        metricas, problemas = [], []
        pesos = {
            "title": 10, "notes": 25, "tags": 15, "license_id": 10,
            "organization": 10, "metadata_modified": 15, "frequency": 10, "resources": 5,
        }
        peso_total = sum(pesos.values())
        ganado, ausentes = 0.0, []
        for campo, peso in pesos.items():
            if self._meta_valor_presente(metadata, campo):
                if campo == "notes":
                    notas = str(metadata.get(campo, ""))
                    ganado += peso * min(1.0, len(notas) / 120.0)
                elif campo == "tags":
                    tags = metadata.get("tags") or []
                    factor = min(1.0, len(tags) / 3.0) if isinstance(tags, (list, tuple)) else 1.0
                    ganado += peso * factor
                else:
                    ganado += peso
            else:
                ausentes.append(campo)

        score = round(ganado / peso_total * 100.0, 2)
        aprobado = score >= 80.0
        if ausentes:
            problemas.append(ProblemaDetectado(
                problema_id=hashlib.md5(f"metadatos_{dataset_id}".encode()).hexdigest()[:12],
                dataset_id=dataset_id, recurso_id=recurso_id,
                categoria=CategoriaProblema.TRAZABILIDAD,
                severidad=SeveridadProblema.ALTA if not aprobado else SeveridadProblema.MEDIA,
                marco_referencia=MarcoReferencia.DAMA_DMBOK,
                titulo="Metadatos del dataset incompletos",
                descripcion=f"Campos ausentes o vacios: {', '.join(ausentes)}.",
                recomendacion="Completar CKAN (descripcion >=120 chars, >=3 tags, licencia, frecuencia).",
            ))
        metricas.append(MetricaCalidad(
            "calidad_metadatos", CategoriaProblema.TRAZABILIDAD, MarcoReferencia.DAMA_DMBOK,
            score, 80.0, aprobado,
            detalles={"ausentes": ausentes, "campos_evaluados": list(pesos.keys())},
        ))
        return metricas, problemas

    def _evaluar_interoperabilidad(self, df: pd.DataFrame, dataset_id: str, recurso_id: str) -> Tuple[List[MetricaCalidad], List[ProblemaDetectado]]:
        metricas, problemas = [], []
        columnas_estandar = {"cve_ent", "cve_mun", "cve_loc", "cvegeo"}
        cols_lower = [c.lower() for c in df.columns]
        usa_claves_std = any(c in cols_lower for c in columnas_estandar)

        if not usa_claves_std:
            tiene_geo = any(k in ' '.join(cols_lower) for k in ["municipio", "estado", "latitud", "longitud"])
            if tiene_geo:
                problemas.append(ProblemaDetectado(
                    problema_id=hashlib.md5(f"interop_claves_{dataset_id}".encode()).hexdigest()[:12],
                    dataset_id=dataset_id, recurso_id=recurso_id,
                    categoria=CategoriaProblema.CONFORMIDAD, severidad=SeveridadProblema.MEDIA,
                    marco_referencia=MarcoReferencia.DAMA_DMBOK, titulo="Falta de claves geográficas estándar",
                    descripcion="El dataset tiene campos geográficos pero no usa claves estándar INEGI.",
                    recomendacion="Incluir columnas 'cve_ent' y 'cve_mun' para fácil cruce de datos."
                ))

        score = 100.0 - (20.0 if not usa_claves_std else 0.0)
        metricas.append(MetricaCalidad(
            nombre="interoperabilidad", categoria=CategoriaProblema.CONFORMIDAD,
            marco_referencia=MarcoReferencia.DAMA_DMBOK, valor=max(0, score),
            umbral_aceptable=70.0, aprobado=score >= 70.0
        ))
        return metricas, problemas

# ============================================================
# ORQUESTADOR PRINCIPAL DE SKILL 2
# ============================================================

class SkillEvaluadorDatos:
    """Clase principal orquestadora del análisis de calidad de los datos."""
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger("SkillEvaluador")
        self.iso25012 = AnalizadorISO25012()
        self.iso8000 = AnalizadorISO8000()
        self.dama = AnalizadorDAMA()
        self.ia_semantica = AnalizadorSemanticoIA()

    def evaluar_catalogo(self, datos_extraidos: Dict, manifiesto: Dict, nivel: NivelAnalisis = NivelAnalisis.ESTANDAR) -> ReporteGlobal:
        """Evalúa todos los datos proporcionados desde la Skill 1."""
        self.logger.info("Iniciando Evaluación de Calidad de Datos Completa")
        reporte_global = ReporteGlobal(
            timestamp_evaluacion=datetime.now(timezone.utc).isoformat(),
            url_catalogo=manifiesto.get("url_origen", "Desconocida")
        )

        for llave, payload in datos_extraidos.items():
            df = payload.get("dataframe")
            metadata = payload.get("metadata", {})
            self.logger.info(f"Evaluando: {metadata.get('titulo_dataset')}")
            
            # Análisis ISO 25012
            m1, p1 = self.iso25012.analizar(df, metadata, nivel)
            # Análisis ISO 8000
            m2, p2 = self.iso8000.analizar(df, metadata, datos_extraidos)
            # Análisis DAMA
            m3, p3 = self.dama.analizar(df, metadata, manifiesto, datos_extraidos)
            # Análisis Semántico IA (Opcional si hay credenciales)
            m4, p4 = self.ia_semantica.analizar_discrepancia(df, metadata)

            metricas_totales = m1 + m2 + m3 + ([m4] if m4 else [])
            problemas_totales = p1 + p2 + p3 + p4

            # Consolidar Dataset
            score_25012 = np.mean([m.valor for m in m1]) if m1 else 0
            score_8000 = np.mean([m.valor for m in m2]) if m2 else 0
            score_dama = np.mean([m.valor for m in m3]) if m3 else 0
            
            scores_para_global = [score_25012, score_8000, score_dama]
            score_semantico = None
            if m4:
                score_semantico = m4.valor
                scores_para_global.append(score_semantico)
                
            score_global = np.mean(scores_para_global)

            clasificacion = (
                "Excelente" if score_global >= 90 else
                "Bueno" if score_global >= 80 else
                "Aceptable" if score_global >= 70 else
                "Deficiente" if score_global >= 50 else "Crítico"
            )

            rep_ds = ReporteDataset(
                dataset_id=metadata.get("dataset_id", "N/A"),
                recurso_id=metadata.get("recurso_id", "N/A"),
                titulo=metadata.get("titulo_dataset", "N/A"),
                organizacion=metadata.get("organizacion", "N/A"),
                score_global=round(score_global, 2),
                score_iso_25012=round(score_25012, 2),
                score_iso_8000=round(score_8000, 2),
                score_dama=round(score_dama, 2),
                score_ia_semantica=round(score_semantico, 2) if score_semantico is not None else None,
                metricas=metricas_totales,
                problemas=problemas_totales,
                clasificacion=clasificacion
            )
            reporte_global.reportes_datasets.append(rep_ds)
            
            reporte_global.total_problemas_detectados += len(problemas_totales)
            for p in problemas_totales:
                reporte_global.problemas_por_severidad[p.severidad.value] = reporte_global.problemas_por_severidad.get(p.severidad.value, 0) + 1
                reporte_global.problemas_por_categoria[p.categoria.value] = reporte_global.problemas_por_categoria.get(p.categoria.value, 0) + 1

        reporte_global.total_datasets_evaluados = len(datos_extraidos)
        
        # Calcular estadísticas globales agregadas para el Dashboard
        if reporte_global.reportes_datasets:
            # Score promedio global
            reporte_global.score_promedio_catalogo = round(np.mean([r.score_global for r in reporte_global.reportes_datasets]), 2)
            
            # Distribución de Clasificación (Excelente, Bueno, etc.)
            clasificaciones = [r.clasificacion for r in reporte_global.reportes_datasets]
            reporte_global.distribucion_clasificacion = dict(Counter(clasificaciones))
            
            # Promedio de calidad por Organización (Secretarías)
            org_scores = {}
            for r in reporte_global.reportes_datasets:
                org = r.organizacion or "Desconocida"
                if org not in org_scores:
                    org_scores[org] = []
                org_scores[org].append(r.score_global)
            
            for org, scores in org_scores.items():
                reporte_global.promedio_por_organizacion[org] = round(np.mean(scores), 2)

        self.logger.info("Evaluación de Calidad Completada.")
        return reporte_global
