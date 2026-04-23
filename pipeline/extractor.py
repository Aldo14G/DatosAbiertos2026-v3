"""
SKILL 1: Extractor de Datasets Completos
=========================================
Diseñado para catálogos de datos gubernamentales,
optimizado para el Catálogo de Datos de Nuevo León.
"""

import requests
import pandas as pd
import json
import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from pathlib import Path
import time
import chardet
import re

# ============================================================
# MODELOS DE DATOS
# ============================================================

class FormatoDataset(Enum):
    CSV = "csv"
    JSON = "json"
    XML = "xml"
    XLSX = "xlsx"
    XLS = "xls"
    PDF = "pdf"
    GEOJSON = "geojson"
    KML = "kml"
    SHP = "shapefile"
    API = "api_endpoint"
    HTML_TABLE = "html_table"
    DESCONOCIDO = "unknown"

class EstadoExtraccion(Enum):
    EXITOSO = "successful"
    PARCIAL = "partial"
    FALLIDO = "failed"
    OMITIDO = "skipped"

class TipoPlataforma(Enum):
    CKAN = "ckan"
    SOCRATA = "socrata"
    ARCGIS_OPEN_DATA = "arcgis_open_data"
    JUNAR = "junar"
    CUSTOM = "custom"
    DESCONOCIDO = "unknown"

@dataclass
class RecursoDescubierto:
    """Representa un recurso individual dentro de un dataset."""
    recurso_id: str
    nombre: str
    url_descarga: str
    formato: FormatoDataset
    tamano_bytes: Optional[int] = None
    ultima_modificacion: Optional[str] = None
    descripcion: Optional[str] = None
    mimetype: Optional[str] = None

@dataclass
class DatasetDescubierto:
    """Representa un dataset completo con todos sus recursos."""
    dataset_id: str
    nombre: str
    titulo: str
    descripcion: Optional[str] = None
    organizacion: Optional[str] = None
    categoria: Optional[str] = None
    etiquetas: List[str] = field(default_factory=list)
    licencia: Optional[str] = None
    frecuencia_actualizacion: Optional[str] = None
    fecha_creacion: Optional[str] = None
    fecha_modificacion: Optional[str] = None
    recursos: List[RecursoDescubierto] = field(default_factory=list)
    metadatos_extra: Dict[str, Any] = field(default_factory=dict)
    url_origen: Optional[str] = None

@dataclass
class ResultadoExtraccionRecurso:
    """Resultado de la extracción de un recurso individual."""
    recurso_id: str
    dataset_id: str
    estado: EstadoExtraccion
    formato_detectado: FormatoDataset
    registros_extraidos: int = 0
    columnas: List[str] = field(default_factory=list)
    tamano_bytes_descargado: int = 0
    hash_contenido: Optional[str] = None
    encoding_detectado: Optional[str] = None
    datos: Optional[Any] = None  # DataFrame o estructura de datos
    errores: List[str] = field(default_factory=list)
    advertencias: List[str] = field(default_factory=list)
    timestamp_extraccion: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    tiempo_extraccion_seg: float = 0.0

@dataclass
class ManifiestoExtraccion:
    """Manifiesto completo de la extracción."""
    url_origen: str
    plataforma_detectada: TipoPlataforma
    timestamp_inicio: str
    timestamp_fin: Optional[str] = None
    total_datasets_descubiertos: int = 0
    total_recursos_descubiertos: int = 0
    total_datasets_extraidos: int = 0
    total_recursos_extraidos: int = 0
    total_registros_extraidos: int = 0
    total_bytes_descargados: int = 0
    datasets_exitosos: int = 0
    datasets_parciales: int = 0
    datasets_fallidos: int = 0
    resultados: List[ResultadoExtraccionRecurso] = field(default_factory=list)
    errores_globales: List[str] = field(default_factory=list)
    version_skill: str = "1.0.0"

# ============================================================
# DETECTOR DE PLATAFORMA
# ============================================================

class DetectorPlataforma:
    """Detecta el tipo de plataforma del catálogo de datos."""

    FIRMAS_CKAN = [
        "/api/3/action/",
        "ckan",
        "data-module=\"hdx\"",
        "/fanstatic/",
    ]

    FIRMAS_SOCRATA = [
        "socrata",
        "/resource/",
        "api.us.socrata.com",
        "Tyler Data & Insights",
    ]

    FIRMAS_JUNAR = [
        "junar",
        "/api/v2/datasets",
    ]

    FIRMAS_ARCGIS = [
        "opendata.arcgis.com",
        "hub.arcgis.com",
        "ArcGIS Hub",
    ]

    @staticmethod
    def detectar(url: str, timeout: int = 30) -> Tuple[TipoPlataforma, Dict]:
        """Detecta la plataforma del catálogo de datos."""
        info = {"api_base": None, "version": None}

        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        ckan_endpoints = [
            f"{base_url}/api/3/action/site_read",
            f"{base_url}/api/3/action/status_show",
            f"{base_url}/api/action/site_read",
        ]

        for endpoint in ckan_endpoints:
            try:
                resp = requests.get(endpoint, timeout=timeout, verify=True)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("success") is True:
                        info["api_base"] = f"{base_url}/api/3/action"
                        info["version"] = "3"
                        return TipoPlataforma.CKAN, info
            except Exception:
                continue

        socrata_endpoint = f"{base_url}/api/catalog/v1"
        try:
            resp = requests.get(socrata_endpoint, timeout=timeout)
            if resp.status_code == 200:
                info["api_base"] = f"{base_url}/api"
                return TipoPlataforma.SOCRATA, info
        except Exception:
            pass

        try:
            resp = requests.get(url, timeout=timeout)
            contenido = resp.text.lower()

            for firma in DetectorPlataforma.FIRMAS_CKAN:
                if firma.lower() in contenido:
                    info["api_base"] = f"{base_url}/api/3/action"
                    return TipoPlataforma.CKAN, info

            for firma in DetectorPlataforma.FIRMAS_SOCRATA:
                if firma.lower() in contenido:
                    info["api_base"] = f"{base_url}/api"
                    return TipoPlataforma.SOCRATA, info

            for firma in DetectorPlataforma.FIRMAS_JUNAR:
                if firma.lower() in contenido:
                    return TipoPlataforma.JUNAR, info

            for firma in DetectorPlataforma.FIRMAS_ARCGIS:
                if firma.lower() in contenido:
                    return TipoPlataforma.ARCGIS_OPEN_DATA, info

        except Exception:
            pass

        return TipoPlataforma.DESCONOCIDO, info

# ============================================================
# EXTRACTORES POR PLATAFORMA
# ============================================================

class ExtractorCKAN:
    """Extractor especializado para plataformas CKAN."""

    def __init__(self, api_base: str, timeout: int = 60):
        self.api_base = api_base.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "DataExtractor-NL/1.0 (Gobierno Abierto)"
        })
        self.logger = logging.getLogger("ExtractorCKAN")

    def _llamar_api(self, action: str, params: Dict = None) -> Dict:
        """Llamada genérica a la API de CKAN."""
        url = f"{self.api_base}/{action}"
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            if data.get("success"):
                return data.get("result", {})
            else:
                raise Exception(
                    f"API CKAN error: {data.get('error', 'Unknown')}"
                )
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error llamando {url}: {e}")
            raise

    def descubrir_datasets(self, limite: int = 0) -> List[DatasetDescubierto]:
        """Descubre datasets disponibles en el catálogo, respetando el límite opcional."""
        datasets = []
        offset = 0
        batch_limit = 100

        self.logger.info("Obteniendo lista de datasets...")
        try:
            # Intentar obtener la lista completa de nombres primero
            lista_completa = self._llamar_api(
                "package_list", {"limit": 100000}
            )
            total_disponible = len(lista_completa)
            self.logger.info(
                f"Total de datasets en catálogo: {total_disponible}"
            )
            
            # Si hay límite, solo procesamos los primeros N nombres
            nombres_a_procesar = lista_completa
            if limite > 0:
                nombres_a_procesar = lista_completa[:limite]
                self.logger.info(f"Limitando descubrimiento a los primeros {limite} datasets.")

            for i, nombre_dataset in enumerate(nombres_a_procesar):
                try:
                    detalle = self._llamar_api(
                        "package_show", {"id": nombre_dataset}
                    )
                    dataset = self._parsear_dataset_ckan(detalle)
                    datasets.append(dataset)

                    if (i + 1) % 50 == 0:
                        self.logger.info(
                            f"Descubiertos {i+1}/{len(nombres_a_procesar)} datasets"
                        )
                    time.sleep(0.1)
                except Exception as e:
                    self.logger.warning(
                        f"Error obteniendo dataset '{nombre_dataset}': {e}"
                    )
                    continue
        except Exception:
            # Fallback a package_search si package_list falla
            self.logger.info("Fallback a package_search...")
            count_resp = self._llamar_api(
                "package_search", {"rows": 0}
            )
            total_esperado = count_resp.get("count", 0)
            
            a_descubrir = total_esperado
            if limite > 0:
                a_descubrir = min(limite, total_esperado)

            while len(datasets) < a_descubrir:
                try:
                    rows = min(batch_limit, a_descubrir - len(datasets))
                    resultado = self._llamar_api(
                        "package_search",
                        {"rows": rows, "start": offset}
                    )
                    resultados_pagina = resultado.get("results", [])

                    if not resultados_pagina:
                        break

                    for detalle in resultados_pagina:
                        dataset = self._parsear_dataset_ckan(detalle)
                        datasets.append(dataset)
                        if len(datasets) >= a_descubrir:
                            break

                    offset += batch_limit
                    self.logger.info(
                        f"Descubiertos {len(datasets)}/{a_descubrir}"
                    )
                    time.sleep(0.3)

                except Exception as e:
                    self.logger.error(f"Error en paginación offset={offset}: {e}")
                    break

        return datasets

    def _parsear_dataset_ckan(self, raw: Dict) -> DatasetDescubierto:
        """Convierte respuesta CKAN cruda a modelo DatasetDescubierto."""
        recursos = []
        for r in raw.get("resources", []):
            formato_str = (r.get("format", "") or "").upper().strip()
            formato = self._mapear_formato(formato_str)

            recurso = RecursoDescubierto(
                recurso_id=r.get("id", ""),
                nombre=r.get("name", r.get("description", "Sin nombre")),
                url_descarga=r.get("url", ""),
                formato=formato,
                tamano_bytes=r.get("size"),
                ultima_modificacion=r.get("last_modified") or r.get("created"),
                descripcion=r.get("description", ""),
                mimetype=r.get("mimetype", ""),
            )
            recursos.append(recurso)

        org = raw.get("organization", {})
        org_nombre = org.get("title", org.get("name", "")) if org else ""

        etiquetas = [
            t.get("display_name", t.get("name", ""))
            for t in raw.get("tags", [])
        ]

        grupos = raw.get("groups", [])
        categoria = (
            grupos[0].get("display_name", grupos[0].get("title", ""))
            if grupos else None
        )

        return DatasetDescubierto(
            dataset_id=raw.get("id", ""),
            nombre=raw.get("name", ""),
            titulo=raw.get("title", ""),
            descripcion=raw.get("notes", ""),
            organizacion=org_nombre,
            categoria=categoria,
            etiquetas=etiquetas,
            licencia=raw.get("license_title", ""),
            frecuencia_actualizacion=raw.get("frequency", raw.get("extras", {})),
            fecha_creacion=raw.get("metadata_created", ""),
            fecha_modificacion=raw.get("metadata_modified", ""),
            recursos=recursos,
            metadatos_extra={
                k: v for k, v in raw.items()
                if k not in [
                    "resources", "organization", "tags",
                    "groups", "id", "name", "title", "notes"
                ]
            },
            url_origen=raw.get("url", ""),
        )

    @staticmethod
    def _mapear_formato(formato_str: str) -> FormatoDataset:
        """Mapea string de formato a enum."""
        mapa = {
            "CSV": FormatoDataset.CSV,
            "JSON": FormatoDataset.JSON,
            "XML": FormatoDataset.XML,
            "XLSX": FormatoDataset.XLSX,
            "XLS": FormatoDataset.XLS,
            "PDF": FormatoDataset.PDF,
            "GEOJSON": FormatoDataset.GEOJSON,
            "KML": FormatoDataset.KML,
            "SHP": FormatoDataset.SHP,
            "SHAPEFILE": FormatoDataset.SHP,
            "API": FormatoDataset.API,
            ".CSV": FormatoDataset.CSV,
        }
        return mapa.get(formato_str, FormatoDataset.DESCONOCIDO)

# ============================================================
# MOTOR DE DESCARGA Y PARSEO
# ============================================================

class MotorDescarga:
    """Motor de descarga y parseo de recursos individuales."""

    MAX_TAMANO_BYTES = 500 * 1024 * 1024  # 500 MB por recurso
    CHUNK_SIZE = 8192

    def __init__(self, directorio_cache: str = "./cache_extraccion"):
        self.directorio_cache = Path(directorio_cache)
        self.directorio_cache.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "DataExtractor-NL/1.0"
        })
        self.logger = logging.getLogger("MotorDescarga")

    def extraer_recurso(
        self, recurso: RecursoDescubierto, dataset_id: str
    ) -> ResultadoExtraccionRecurso:
        """Extrae y parsea un recurso individual."""
        inicio = time.time()
        resultado = ResultadoExtraccionRecurso(
            recurso_id=recurso.recurso_id,
            dataset_id=dataset_id,
            estado=EstadoExtraccion.FALLIDO,
            formato_detectado=recurso.formato,
        )

        try:
            contenido, info_descarga = self._descargar(recurso.url_descarga)

            if contenido is None:
                resultado.errores.append("No se pudo descargar el recurso")
                return resultado

            resultado.tamano_bytes_descargado = len(contenido)
            resultado.hash_contenido = hashlib.sha256(contenido).hexdigest()

            if recurso.formato in [
                FormatoDataset.CSV, FormatoDataset.JSON,
                FormatoDataset.XML, FormatoDataset.HTML_TABLE
            ]:
                deteccion = chardet.detect(contenido[:10000])
                resultado.encoding_detectado = deteccion.get("encoding", "utf-8")

            resultado = self._parsear_contenido(
                contenido, recurso.formato, resultado
            )

            if resultado.registros_extraidos > 0:
                resultado.estado = EstadoExtraccion.EXITOSO
            elif resultado.datos is not None:
                resultado.estado = EstadoExtraccion.PARCIAL

        except Exception as e:
            resultado.errores.append(f"Error general: {str(e)}")
            resultado.estado = EstadoExtraccion.FALLIDO

        resultado.tiempo_extraccion_seg = round(time.time() - inicio, 3)
        return resultado

    def _descargar(
        self, url: str
    ) -> Tuple[Optional[bytes], Dict]:
        """Descarga el contenido de una URL con manejo de errores."""
        info = {"status_code": None, "content_type": None}

        try:
            head = self.session.head(url, timeout=30, allow_redirects=True)
            content_length = int(head.headers.get("Content-Length", 0))

            if content_length > self.MAX_TAMANO_BYTES:
                self.logger.warning(
                    f"Recurso excede límite: {content_length / 1024 / 1024:.1f} MB"
                )
                return None, info

            resp = self.session.get(
                url, timeout=120, allow_redirects=True, stream=True
            )
            resp.raise_for_status()

            info["status_code"] = resp.status_code
            info["content_type"] = resp.headers.get("Content-Type", "")

            contenido = b""
            for chunk in resp.iter_content(chunk_size=self.CHUNK_SIZE):
                contenido += chunk
                if len(contenido) > self.MAX_TAMANO_BYTES:
                    self.logger.warning("Descarga truncada por límite")
                    break

            return contenido, info

        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout descargando: {url}")
            return None, info
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error descargando {url}: {e}")
            return None, info

    def _parsear_contenido(
        self,
        contenido: bytes,
        formato: FormatoDataset,
        resultado: ResultadoExtraccionRecurso,
    ) -> ResultadoExtraccionRecurso:
        """Parsea el contenido descargado según su formato."""
        encoding = resultado.encoding_detectado or "utf-8"

        try:
            if formato == FormatoDataset.CSV:
                resultado = self._parsear_csv(contenido, encoding, resultado)
            elif formato == FormatoDataset.JSON:
                resultado = self._parsear_json(contenido, encoding, resultado)
            elif formato in (FormatoDataset.XLSX, FormatoDataset.XLS):
                resultado = self._parsear_excel(contenido, resultado)
            elif formato == FormatoDataset.XML:
                resultado = self._parsear_xml(contenido, encoding, resultado)
            elif formato == FormatoDataset.GEOJSON:
                resultado = self._parsear_geojson(contenido, encoding, resultado)
            elif formato == FormatoDataset.PDF:
                resultado.advertencias.append("Formato PDF: extracción de tablas limitada")
                resultado.estado = EstadoExtraccion.OMITIDO
            else:
                resultado.advertencias.append(f"Formato {formato.value} no soportado para parseo")
        except Exception as e:
            resultado.errores.append(f"Error parseando {formato.value}: {e}")

        return resultado

    def _parsear_csv(
        self, contenido: bytes, encoding: str,
        resultado: ResultadoExtraccionRecurso
    ) -> ResultadoExtraccionRecurso:
        """Parsea contenido CSV con detección automática de delimitador."""
        from io import StringIO
        import csv

        texto = contenido.decode(encoding, errors="replace")

        try:
            muestra = texto[:5000]
            dialect = csv.Sniffer().sniff(muestra)
            separador = dialect.delimiter
        except csv.Error:
            separador = ","

        try:
            try:
                df = pd.read_csv(
                    StringIO(texto),
                    sep=separador,
                    engine="pyarrow",
                    dtype_backend="pyarrow",
                    column_names=None if isinstance(separador, str) else [] # PyArrow might throw if bad options. Just keep it simple
                )
            except Exception:
                df = pd.read_csv(
                    StringIO(texto),
                    sep=separador,
                    on_bad_lines="warn",
                )

            resultado.datos = df
            resultado.registros_extraidos = len(df)
            resultado.columnas = df.columns.tolist()
            resultado.estado = EstadoExtraccion.EXITOSO
        except Exception as e:
            for enc_alt in ["latin-1", "iso-8859-1", "cp1252", "utf-8-sig"]:
                try:
                    texto_alt = contenido.decode(enc_alt, errors="replace")
                    try:
                        df = pd.read_csv(
                            StringIO(texto_alt),
                            sep=separador,
                            engine="pyarrow",
                            dtype_backend="pyarrow"
                        )
                    except Exception:
                        df = pd.read_csv(
                            StringIO(texto_alt),
                            sep=separador,
                            on_bad_lines="skip",
                        )
                    resultado.datos = df
                    resultado.registros_extraidos = len(df)
                    resultado.columnas = df.columns.tolist()
                    resultado.encoding_detectado = enc_alt
                    resultado.advertencias.append(f"Encoding ajustado a {enc_alt}")
                    resultado.estado = EstadoExtraccion.EXITOSO
                    break
                except Exception:
                    continue
            else:
                resultado.errores.append(f"CSV no parseable: {e}")

        return resultado

    def _parsear_json(
        self, contenido: bytes, encoding: str,
        resultado: ResultadoExtraccionRecurso
    ) -> ResultadoExtraccionRecurso:
        """Parsea contenido JSON."""
        texto = contenido.decode(encoding, errors="replace")
        data = json.loads(texto)

        if isinstance(data, list):
            df = pd.json_normalize(data, max_level=3)
            resultado.datos = df
            resultado.registros_extraidos = len(df)
            resultado.columnas = df.columns.tolist()
        elif isinstance(data, dict):
            arrays_encontrados = {}
            for key, value in data.items():
                if isinstance(value, list) and len(value) > 0:
                    arrays_encontrados[key] = value

            if arrays_encontrados:
                key_principal = max(arrays_encontrados, key=lambda k: len(arrays_encontrados[k]))
                df = pd.json_normalize(arrays_encontrados[key_principal], max_level=3)
                resultado.datos = df
                resultado.registros_extraidos = len(df)
                resultado.columnas = df.columns.tolist()
                resultado.advertencias.append(f"Extraída clave principal: '{key_principal}'")
            else:
                df = pd.json_normalize([data])
                resultado.datos = df
                resultado.registros_extraidos = 1
                resultado.columnas = df.columns.tolist()

        resultado.estado = EstadoExtraccion.EXITOSO
        return resultado

    def _parsear_excel(
        self, contenido: bytes,
        resultado: ResultadoExtraccionRecurso
    ) -> ResultadoExtraccionRecurso:
        """Parsea archivos Excel (todas las hojas)."""
        from io import BytesIO

        todas_hojas = pd.read_excel(
            BytesIO(contenido), sheet_name=None, engine="openpyxl"
        )

        if len(todas_hojas) == 1:
            nombre_hoja = list(todas_hojas.keys())[0]
            df = todas_hojas[nombre_hoja]
        else:
            hoja_principal = max(todas_hojas, key=lambda k: len(todas_hojas[k]))
            df = todas_hojas[hoja_principal]
            resultado.advertencias.append(
                f"Excel con {len(todas_hojas)} hojas. Principal: '{hoja_principal}'."
            )

        resultado.datos = df
        resultado.registros_extraidos = len(df)
        resultado.columnas = df.columns.tolist()
        resultado.estado = EstadoExtraccion.EXITOSO
        return resultado

    def _parsear_xml(
        self, contenido: bytes, encoding: str,
        resultado: ResultadoExtraccionRecurso
    ) -> ResultadoExtraccionRecurso:
        """Parsea contenido XML."""
        from io import BytesIO

        try:
            df = pd.read_xml(BytesIO(contenido))
            resultado.datos = df
            resultado.registros_extraidos = len(df)
            resultado.columnas = df.columns.tolist()
            resultado.estado = EstadoExtraccion.EXITOSO
        except Exception:
            soup = BeautifulSoup(contenido, "lxml-xml")
            registros = []
            elementos = soup.find_all(True)
            tag_counts = {}
            for elem in elementos:
                tag_counts[elem.name] = tag_counts.get(elem.name, 0) + 1

            if tag_counts:
                tag_principal = max(tag_counts, key=tag_counts.get)
                for elem in soup.find_all(tag_principal):
                    registro = {}
                    for child in elem.children:
                        if hasattr(child, "name") and child.name:
                            registro[child.name] = child.get_text(strip=True)
                    if registro:
                        registros.append(registro)

                if registros:
                    df = pd.DataFrame(registros)
                    resultado.datos = df
                    resultado.registros_extraidos = len(df)
                    resultado.columnas = df.columns.tolist()

        return resultado

    def _parsear_geojson(
        self, contenido: bytes, encoding: str,
        resultado: ResultadoExtraccionRecurso
    ) -> ResultadoExtraccionRecurso:
        """Parsea contenido GeoJSON."""
        texto = contenido.decode(encoding, errors="replace")
        data = json.loads(texto)

        features = data.get("features", [])
        registros = []
        for feature in features:
            registro = feature.get("properties", {}).copy()
            geometry = feature.get("geometry", {})
            registro["geometry_type"] = geometry.get("type", "")
            registro["geometry_coordinates"] = json.dumps(geometry.get("coordinates", []))
            registros.append(registro)

        if registros:
            df = pd.DataFrame(registros)
            resultado.datos = df
            resultado.registros_extraidos = len(df)
            resultado.columnas = df.columns.tolist()

        resultado.estado = EstadoExtraccion.EXITOSO
        return resultado

# ============================================================
# VALIDADOR DE COMPLETITUD
# ============================================================

class ValidadorCompletitud:
    """Valida que la extracción sea completa y consistente."""

    @staticmethod
    def validar(
        datasets_descubiertos: List[DatasetDescubierto],
        resultados: List[ResultadoExtraccionRecurso],
        manifiesto: ManifiestoExtraccion,
    ) -> Dict[str, Any]:
        """Ejecuta validación completa de la extracción."""
        reporte = {
            "validacion_timestamp": datetime.now(timezone.utc).isoformat(),
            "completitud_global": {},
            "validaciones_detalladas": [],
            "alertas": [],
            "aprobado": True,
        }

        total_descubiertos = len(datasets_descubiertos)
        ids_descubiertos = {d.dataset_id for d in datasets_descubiertos}
        ids_extraidos = {r.dataset_id for r in resultados}
        ids_exitosos = {r.dataset_id for r in resultados if r.estado == EstadoExtraccion.EXITOSO}

        cobertura = (len(ids_extraidos) / total_descubiertos * 100 if total_descubiertos > 0 else 0)
        tasa_exito = (len(ids_exitosos) / len(ids_extraidos) * 100 if ids_extraidos else 0)

        reporte["completitud_global"] = {
            "datasets_descubiertos": total_descubiertos,
            "datasets_intentados": len(ids_extraidos),
            "datasets_exitosos": len(ids_exitosos),
            "cobertura_porcentaje": round(cobertura, 2),
            "tasa_exito_porcentaje": round(tasa_exito, 2),
            "datasets_faltantes": list(ids_descubiertos - ids_extraidos),
        }

        if cobertura < 95:
            reporte["alertas"].append({
                "tipo": "COBERTURA_BAJA",
                "severidad": "ALTA",
                "mensaje": f"Cobertura de extracción: {cobertura:.1f}% (umbral: 95%)",
            })
            reporte["aprobado"] = False

        for resultado in resultados:
            validacion_recurso = {
                "recurso_id": resultado.recurso_id,
                "dataset_id": resultado.dataset_id,
                "checks": [],
            }

            validacion_recurso["checks"].append({
                "check": "estado_extraccion",
                "resultado": resultado.estado.value,
                "aprobado": resultado.estado == EstadoExtraccion.EXITOSO,
            })

            validacion_recurso["checks"].append({
                "check": "registros_no_vacios",
                "resultado": resultado.registros_extraidos,
                "aprobado": resultado.registros_extraidos > 0,
            })

            validacion_recurso["checks"].append({
                "check": "hash_integridad",
                "resultado": resultado.hash_contenido is not None,
                "aprobado": resultado.hash_contenido is not None,
            })

            tiene_errores = len(resultado.errores) > 0
            validacion_recurso["checks"].append({
                "check": "sin_errores_criticos",
                "resultado": f"{len(resultado.errores)} errores",
                "aprobado": not tiene_errores,
            })

            reporte["validaciones_detalladas"].append(validacion_recurso)

        total_registros = sum(r.registros_extraidos for r in resultados)
        total_bytes = sum(r.tamano_bytes_descargado for r in resultados)

        reporte["completitud_global"]["total_registros"] = total_registros
        reporte["completitud_global"]["total_bytes"] = total_bytes
        reporte["completitud_global"]["total_bytes_legible"] = f"{total_bytes / 1024 / 1024:.2f} MB"

        return reporte

# ============================================================
# ORQUESTADOR PRINCIPAL DE SKILL 1
# ============================================================

class SkillExtractorDatasets:
    """
    Skill principal de extracción de datasets.
    Punto de entrada para el framework multi-agente.
    """

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger("SkillExtractor")
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
        )

    def ejecutar(self, url: str, limite_datasets: int = 0) -> Dict[str, Any]:
        """Punto de entrada principal."""
        self.logger.info(f"═══ INICIANDO EXTRACCIÓN: {url} ═══")

        manifiesto = ManifiestoExtraccion(
            url_origen=url,
            plataforma_detectada=TipoPlataforma.DESCONOCIDO,
            timestamp_inicio=datetime.now(timezone.utc).isoformat(),
        )

        self.logger.info("FASE 1: Detectando plataforma...")
        tipo_plataforma, info_plataforma = DetectorPlataforma.detectar(url)
        manifiesto.plataforma_detectada = tipo_plataforma
        self.logger.info(f"Plataforma detectada: {tipo_plataforma.value}")

        self.logger.info("FASE 2: Descubriendo datasets...")
        datasets_descubiertos = self._descubrir(tipo_plataforma, info_plataforma, url, limite=limite_datasets)
        
        # Aplicar límite si se especifica
        if limite_datasets > 0:
            datasets_descubiertos = datasets_descubiertos[:limite_datasets]
            self.logger.info(f"Límite aplicado: {limite_datasets} datasets.")

        manifiesto.total_datasets_descubiertos = len(datasets_descubiertos)
        manifiesto.total_recursos_descubiertos = sum(len(d.recursos) for d in datasets_descubiertos)
        self.logger.info(
            f"Procesando: {manifiesto.total_datasets_descubiertos} datasets, "
            f"{manifiesto.total_recursos_descubiertos} recursos"
        )

        self.logger.info("FASE 3: Extrayendo recursos...")
        motor = MotorDescarga()
        resultados = []

        for i, dataset in enumerate(datasets_descubiertos):
            self.logger.info(f"Procesando dataset {i+1}/{len(datasets_descubiertos)}: {dataset.titulo}")

            # SELECCIÓN DE RECURSO: Priorizar datos reales sobre diccionarios
            mejor_recurso = self._seleccionar_mejor_recurso(dataset.recursos)
            
            if mejor_recurso:
                self.logger.info(f"  -> Extrayendo mejor recurso: {mejor_recurso.nombre} ({mejor_recurso.formato.value})")
                resultado = motor.extraer_recurso(mejor_recurso, dataset.dataset_id)
                resultados.append(resultado)

                if resultado.estado == EstadoExtraccion.EXITOSO:
                    manifiesto.datasets_exitosos += 1
                elif resultado.estado == EstadoExtraccion.PARCIAL:
                    manifiesto.datasets_parciales += 1
                else:
                    manifiesto.datasets_fallidos += 1
            else:
                self.logger.warning(f"  x No se encontró recurso apto para extraction en {dataset.titulo}")

            time.sleep(0.3)

        manifiesto.resultados = resultados
        manifiesto.total_datasets_extraidos = len({r.dataset_id for r in resultados})
        manifiesto.total_recursos_extraidos = len(resultados)
        manifiesto.total_registros_extraidos = sum(r.registros_extraidos for r in resultados)
        manifiesto.total_bytes_descargados = sum(r.tamano_bytes_descargado for r in resultados)

        self.logger.info("FASE 4: Validando completitud...")
        reporte_validacion = ValidadorCompletitud.validar(
            datasets_descubiertos, resultados, manifiesto
        )

        manifiesto.timestamp_fin = datetime.now(timezone.utc).isoformat()

        output = {
            "manifiesto": asdict(manifiesto),
            "datasets_descubiertos": [asdict(d) for d in datasets_descubiertos],
            "resultados_extraccion": self._serializar_resultados(resultados),
            "validacion_completitud": reporte_validacion,
            "datos_extraidos": self._empaquetar_datos(resultados, datasets_descubiertos),
        }

        self.logger.info("═══ EXTRACCIÓN COMPLETADA ═══")
        self.logger.info(f"  Datasets: {manifiesto.total_datasets_extraidos}")
        return output

    def _seleccionar_mejor_recurso(self, recursos: List[RecursoDescubierto]) -> Optional[RecursoDescubierto]:
        """
        Selecciona el recurso con más probabilidad de ser el dataset principal.
        Evita PDFs, diccionarios y metadatos.
        """
        if not recursos:
            return None

        # 1. Filtrar formatos soportados y no PDF
        candidatos = [
            r for r in recursos 
            if r.formato not in [FormatoDataset.PDF, FormatoDataset.DESCONOCIDO]
        ]
        
        if not candidatos:
            return None

        # 2. Puntuación de candidatos
        def puntuar(r: RecursoDescubierto) -> float:
            score = 0.0
            nombre_desc = (r.nombre + " " + (r.descripcion or "")).lower()
            
            # Formatos preferidos
            if r.formato == FormatoDataset.CSV: score += 50
            elif r.formato == FormatoDataset.XLSX: score += 40
            elif r.formato == FormatoDataset.JSON: score += 30
            
            # Penalizar diccionarios/metadatos
            keywords_ruido = ["diccionario", "glosario", "metadatos", "estructura", "catalogo", "catalogos"]
            if any(k in nombre_desc for k in keywords_ruido):
                score -= 100
                
            # Bonus por tamaño (si está disponible)
            if r.tamano_bytes:
                score += min(20, r.tamano_bytes / 1024 / 1024) # Max 20 pts por MB
                
            return score

        candidatos.sort(key=puntuar, reverse=True)
        return candidatos[0]

    def _descubrir(self, plataforma: TipoPlataforma, info: Dict, url: str, limite: int = 0) -> List[DatasetDescubierto]:
        if plataforma == TipoPlataforma.CKAN:
            extractor = ExtractorCKAN(info["api_base"])
            return extractor.descubrir_datasets(limite=limite)
        else:
            parsed = urlparse(url)
            base = f"{parsed.scheme}://{parsed.netloc}/api/3/action"
            extractor = ExtractorCKAN(base)
            try:
                return extractor.descubrir_datasets(limite=limite)
            except Exception as e:
                self.logger.error(f"Fallback CKAN falló: {e}")
                return []

    def _serializar_resultados(self, resultados: List[ResultadoExtraccionRecurso]) -> List[Dict]:
        return [{
            "recurso_id": r.recurso_id, "dataset_id": r.dataset_id,
            "estado": r.estado.value, "formato_detectado": r.formato_detectado.value,
            "registros_extraidos": r.registros_extraidos, "columnas": r.columnas,
            "tamano_bytes_descargado": r.tamano_bytes_descargado, "hash_contenido": r.hash_contenido,
            "encoding_detectado": r.encoding_detectado, "errores": r.errores,
            "advertencias": r.advertencias, "timestamp_extraccion": r.timestamp_extraccion,
            "tiempo_extraccion_seg": r.tiempo_extraccion_seg,
        } for r in resultados]

    def _empaquetar_datos(
        self, resultados: List[ResultadoExtraccionRecurso], datasets: List[DatasetDescubierto]
    ) -> Dict[str, Any]:
        dataset_map = {d.dataset_id: d for d in datasets}
        paquete = {}

        for resultado in resultados:
            if resultado.datos is None:
                continue

            dataset_info = dataset_map.get(resultado.dataset_id)
            clave = f"{resultado.dataset_id}__{resultado.recurso_id}"

            paquete[clave] = {
                "dataframe": resultado.datos,
                "metadata": {
                    "dataset_id": resultado.dataset_id, "recurso_id": resultado.recurso_id,
                    "titulo_dataset": dataset_info.titulo if dataset_info else "",
                    "descripcion": dataset_info.descripcion if dataset_info else "",
                    "organizacion": dataset_info.organizacion if dataset_info else "",
                    "categoria": dataset_info.categoria if dataset_info else "",
                    "formato": resultado.formato_detectado.value,
                    "registros": resultado.registros_extraidos, "columnas": resultado.columnas,
                    "hash": resultado.hash_contenido, "encoding": resultado.encoding_detectado,
                    "timestamp_extraccion": resultado.timestamp_extraccion,
                },
            }

        return paquete
