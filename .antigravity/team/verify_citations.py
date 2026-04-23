"""
verify_citations.py — Rol 1: Arqueólogo de Fuentes
Proyecto: Gobernanza de Datos Abiertos NL 2026

Protocolo de verificación (3 capas):
  1. web_fetch de la URL original
  2. Resolución por DOI oficial (doi.org)
  3. Búsqueda en Semantic Scholar API

Produce: .antigravity/team/shared/fuentes_verificadas.json
"""
import json
import time
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    raise SystemExit("❌ Instala requests: pip install requests")

HEADERS   = {"User-Agent": "DatosAbiertosNL-ResearchBot/1.0 (academic citation verification)"}
TIMEOUT   = 15
DELAY     = 1.5
OUTPUT    = Path(".antigravity/team/shared/fuentes_verificadas.json")

# ── Citas del PDF que requieren verificación ──────────────────
CITAS = [
    {
        "id"    : "nexos-2025",
        "autor" : "Nexos Federalismo",
        "año"   : 2025,
        "titulo": "El nuevo modelo de datos abiertos en México",
        "url"   : "https://federalismo.nexos.com.mx/2025/12/el-nuevo-modelo-de-datos-abiertos-en-mexico/",
        "doi"   : None,
        "query" : "nuevo modelo datos abiertos México Nexos Federalismo 2025",
        "apa7"  : "Nexos Federalismo. (2025, diciembre). El nuevo modelo de datos abiertos en México. https://federalismo.nexos.com.mx/2025/12/el-nuevo-modelo-de-datos-abiertos-en-mexico/",
        "nota_original": "URL podría no existir aún — verificar disponibilidad",
    },
    {
        "id"    : "condatos-2023",
        "autor" : "INAI",
        "año"   : 2023,
        "titulo": "Política Nacional de Datos Abiertos (ConDATOS)",
        "url"   : "https://home.inai.org.mx/",
        "doi"   : None,
        "query" : "ConDATOS Política Nacional Datos Abiertos INAI 2023",
        "apa7"  : "Instituto Nacional de Transparencia, Acceso a la Información y Protección de Datos Personales [INAI]. (2023). Política Nacional de Datos Abiertos (ConDATOS). Gobierno de México.",
        "nota_original": "URL original en PDF era abramos.mx — dominio incorrecto para INAI",
    },
    {
        "id"    : "flores-2024",
        "autor" : "Flores, C., Janssen, M., & Rodríguez Bolívar, M. P.",
        "año"   : 2024,
        "titulo": "Identifying patterns and recommendations for sustainable open data initiatives",
        "url"   : "https://doi.org/10.1016/j.giq.2023.101898",
        "doi"   : "10.1016/j.giq.2023.101898",
        "query" : "Flores Janssen Rodriguez Bolivar sustainable open data initiatives benchmarking 2024",
        "apa7"  : "Flores, C., Janssen, M., & Rodríguez Bolívar, M. P. (2024). Identifying patterns and recommendations of and for sustainable open data initiatives: A benchmarking-driven analysis of open government data initiatives among European countries. Government Information Quarterly, 41(1), artículo 101898. https://doi.org/10.1016/j.giq.2023.101898",
    },
    {
        "id"    : "espinoza-2023",
        "autor" : "Espinoza-Portilla, E., Miraya-Arce, J., & Lucio-Dominguez, R.",
        "año"   : 2023,
        "titulo": "Quality study of open government data related to COVID-19 in Latin America",
        "url"   : "https://doi.org/10.17533/udea.redin.20220107",
        "doi"   : "10.17533/udea.redin.20220107",
        "query" : "Espinoza-Portilla open government data quality COVID Latin America Antioquia 2023",
        "apa7"  : "Espinoza-Portilla, E., Miraya-Arce, J., & Lucio-Dominguez, R. (2023). Quality study of open government data related to COVID-19 in Latin America. Revista Facultad de Ingeniería Universidad de Antioquia, (108), 18–32. https://doi.org/10.17533/udea.redin.20220107",
    },
    {
        "id"    : "zhang-2024",
        "autor" : "Zhang, J., Li, Y., & Wang, X.",
        "año"   : 2024,
        "titulo": "A survey on data quality dimensions and tools for machine learning",
        "url"   : "https://arxiv.org/abs/2406.19614",
        "doi"   : None,
        "query" : "survey data quality dimensions tools machine learning Zhang 2024 arXiv",
        "apa7"  : "Zhang, J., Li, Y., & Wang, X. (2024). A survey on data quality dimensions and tools for machine learning. arXiv preprint, arXiv:2406.19614. https://arxiv.org/abs/2406.19614",
    },
    {
        "id"    : "ocde-ourdata-2023",
        "autor" : "OCDE",
        "año"   : 2023,
        "titulo": "2023 OECD Open Useful and Re-usable data (OURdata) Index",
        "url"   : "https://doi.org/10.1787/a37f51c3-en",
        "doi"   : "10.1787/a37f51c3-en",
        "query" : "OECD OURdata index 2023 open useful reusable government data",
        "apa7"  : "Organización para la Cooperación y el Desarrollo Económicos [OCDE]. (2023). 2023 OECD Open, Useful and Re-usable data (OURdata) Index. OECD Publishing. https://doi.org/10.1787/a37f51c3-en",
    },
    {
        "id"    : "ocde-digital-2024",
        "autor" : "OCDE",
        "año"   : 2024,
        "titulo": "2023 OECD Digital Government Index",
        "url"   : "https://doi.org/10.1787/1a89ed5e-en",
        "doi"   : "10.1787/1a89ed5e-en",
        "query" : "OECD Digital Government Index 2023 public governance policy",
        "apa7"  : "Organización para la Cooperación y el Desarrollo Económicos [OCDE]. (2024b). 2023 OECD Digital Government Index. OECD Public Governance Policy Papers. OECD Publishing. https://doi.org/10.1787/1a89ed5e-en",
    },
    {
        "id"    : "labnl-2024",
        "autor" : "Gómez, O., Lanis, R., & equipo Lab Nuevo León",
        "año"   : 2024,
        "titulo": "¿Cómo vamos en Datos en Nuevo León?",
        "url"   : "https://wiki.labnuevoleon.mx/",
        "doi"   : None,
        "query" : "Cómo vamos datos Nuevo León LabNL 2024 calidad datos abiertos prototipo evaluación",
        "apa7"  : "Gómez, O., Lanis, R., & equipo Lab Nuevo León. (2024). ¿Cómo vamos en Datos en Nuevo León? Prototipo de evaluación de calidad de datos abiertos gubernamentales. WikiLabNL.",
        "nota_original": "URL con caracteres especiales — verificar URL simplificada",
    },
    {
        "id"    : "wang-strong-1996",
        "autor" : "Wang, R. Y., & Strong, D. R.",
        "año"   : 1996,
        "titulo": "Beyond accuracy: What data quality means to data consumers",
        "url"   : "https://doi.org/10.1080/07421222.1996.11518099",
        "doi"   : "10.1080/07421222.1996.11518099",
        "query" : "Wang Strong beyond accuracy data quality consumers JMIS 1996",
        "apa7"  : "Wang, R. Y., & Strong, D. R. (1996). Beyond accuracy: What data quality means to data consumers. Journal of Management Information Systems, 12(4), 5–33. https://doi.org/10.1080/07421222.1996.11518099",
    },
]


def verificar_url(url: str) -> tuple[int, str]:
    """Retorna (status_code, url_final) tras seguir redirects."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        return r.status_code, r.url
    except requests.exceptions.Timeout:
        return 408, url
    except requests.exceptions.ConnectionError:
        return 0, url
    except Exception as e:
        return -1, str(e)[:100]


def buscar_semantic_scholar(query: str, doi: str = None) -> dict:
    """Consulta Semantic Scholar API y devuelve el mejor resultado."""
    try:
        params = {
            "query" : query,
            "fields": "title,authors,year,externalIds,openAccessPdf,url",
            "limit" : 3,
        }
        r = requests.get(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            params=params,
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        if r.status_code != 200:
            return {}
        data = r.json().get("data", [])
        if not data:
            return {}
        # Preferir resultado con DOI coincidente
        for paper in data:
            if doi and paper.get("externalIds", {}).get("DOI","").lower() == doi.lower():
                return paper
        return data[0]
    except Exception:
        return {}


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    resultados = []

    print(f"\n{'='*60}")
    print("  VERIFICADOR DE CITAS — NL 2026")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")

    for c in CITAS:
        print(f"🔍 [{c['id']}] {c['autor'][:40]} ({c['año']})")

        estado, url_final, nota_verif = "UNVERIFIED", c["url"], ""

        # ── Capa 1: URL original ──────────────────────────────
        status_code, resolved_url = verificar_url(c["url"])
        if status_code == 200:
            estado    = "VERIFIED"
            url_final = resolved_url
            nota_verif= "URL original activa (HTTP 200)"
            print(f"   ✓ VERIFIED → {resolved_url[:70]}")
        else:
            print(f"   ✗ HTTP {status_code} — intentando alternativas...")

        # ── Capa 2: DOI oficial ───────────────────────────────
        if estado == "UNVERIFIED" and c.get("doi"):
            doi_url = f"https://doi.org/{c['doi']}"
            sc2, ru2 = verificar_url(doi_url)
            if sc2 == 200:
                estado    = "REPLACED_DOI"
                url_final = ru2
                nota_verif= f"URL original inactiva. DOI resuelve: {ru2[:70]}"
                print(f"   ✓ DOI OK → {ru2[:70]}")

        # ── Capa 3: Semantic Scholar ──────────────────────────
        if estado == "UNVERIFIED":
            paper = buscar_semantic_scholar(c["query"], c.get("doi"))
            if paper:
                oap = paper.get("openAccessPdf") or {}
                ext = paper.get("externalIds")   or {}
                titulo_encontrado = paper.get("title","")[:60]
                if oap.get("url"):
                    estado    = "REPLACED_OA"
                    url_final = oap["url"]
                    nota_verif= f"Open Access encontrado. Título: {titulo_encontrado}"
                    print(f"   ✓ Open Access → {url_final[:70]}")
                elif ext.get("DOI"):
                    new_doi_url = f"https://doi.org/{ext['DOI']}"
                    sc3, _      = verificar_url(new_doi_url)
                    if sc3 == 200:
                        estado    = "REPLACED_SCHOLAR"
                        url_final = new_doi_url
                        nota_verif= f"DOI hallado via Semantic Scholar. Título: {titulo_encontrado}"
                        print(f"   ✓ Scholar DOI → {url_final[:70]}")

        if estado == "UNVERIFIED":
            nota_verif = "No se pudo verificar en 3 capas. Requiere revisión manual."
            print("   ✗ UNVERIFIED — requiere revisión manual")

        resultado = {
            **c,
            "estado"          : estado,
            "url_final"       : url_final,
            "nota_verificacion": nota_verif,
            "verificado_ts"   : datetime.now().isoformat(),
        }
        resultados.append(resultado)
        time.sleep(DELAY)

    # ── Guardar resultados ────────────────────────────────────
    output_data = {
        "proyecto"   : "Gobernanza Datos Abiertos NL 2026",
        "generado"   : datetime.now().isoformat(),
        "total"      : len(resultados),
        "verificadas": sum(1 for r in resultados if r["estado"] != "UNVERIFIED"),
        "fuentes"    : resultados,
    }
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    # ── Resumen final ─────────────────────────────────────────
    v = output_data["verificadas"]
    t = output_data["total"]
    print(f"\n{'='*60}")
    print(f"  RESUMEN: {v}/{t} fuentes verificadas o reemplazadas ({v/t*100:.0f}%)")
    for r in resultados:
        icon = {"VERIFIED":"✓","REPLACED_DOI":"↻","REPLACED_OA":"↻",
                "REPLACED_SCHOLAR":"↻","UNVERIFIED":"✗"}.get(r["estado"],"?")
        print(f"  {icon} [{r['estado']:<18}] {r['id']}")
    print(f"\n  📄 Resultados: {OUTPUT}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
