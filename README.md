# Auditoría de Datos Abiertos — Nuevo León 2026

![Estado](https://img.shields.io/badge/Estado-Producci%C3%B3n-success)
![Python](https://img.shields.io/badge/Python-3.13+-blue)
![Next.js](https://img.shields.io/badge/Next.js-15.0+-black)

Una auditoría visual y completa de la calidad de datos abiertos del Gobierno del Estado de Nuevo León. Evaluamos cada dataset del portal (`catalogodatos.nl.gob.mx`) contra el estándar internacional ISO/IEC 25012:2008 y exponemos los resultados en una landing page moderna, con rankings por dependencia y hallazgos clave.

El proyecto consiste en dos componentes que trabajan juntos pero viven de forma independiente.

## Cómo está construido

**Landing page pública (Next.js 15 + React + Tailwind)**
- Lo que ves es esto. Una página moderna que explica la evaluación, muestra hallazgos clave y vincula al dashboard analítico.
- Hospedado en Firebase Hosting.
- Vive en `landing/`.

**Pipeline de análisis (Python 3.13+)**
- Código que extrae datos del CKAN de Nuevo León, aplica el algoritmo de calidad ISO 25012 y genera los reportes.
- Se ejecuta bajo demanda o en cronograma para actualizar los scores.
- La lógica central está en `pipeline/` y `data_layer.py`. Usa `config.py` para umbrales y pesos.
- Los resultados se sirven a través de API o se exportan como CSV.

## Cómo medimos

Usamos siete dimensiones de ISO/IEC 25012:2008. Cada una tiene un peso:

- Completitud (30%): Datos sin agujeros críticos.
- Exactitud (25%): Los datos dicen la verdad.
- Consistencia (15%): Sin contradicciones internas.
- Unicidad (8%): Sin registros duplicados o fantasma.
- Apertura (8%): Formatos que puedes reutilizar (JSON, CSV).
- Documentación (7%): Diccionarios y metadata clara.
- Actualidad (7%): Qué tan fresco es el dato.

Los datasets caen en tres categorías:

- Oro (≥90): Está bien. Los datos funcionan.
- Plata (70-89): Tienen potencial. Necesitan trabajo técnico.
- Bronce (<70): Rotos. Requieren atención inmediata.

Cada dataset obtiene un puntaje de 0 a 100 según estas dimensiones. Las dependencias también obtienen un promedio.

## Para ejecutar localmente

**Requisitos:** Python 3.13+, Node.js 20+

```bash
# Clonar
git clone https://github.com/Aldo14G/DatosAbiertos2026-v3.git
cd DatosAbiertos2026-v3
```

**Backend Python**
```bash
# Entorno virtual
python -m venv .venv
source .venv/Scripts/activate  # Linux/Mac
# o
.venv\Scripts\activate  # Windows

# Instalar deps
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Actualizar scores (opcional, conecta a CKAN y recalcula todo)
python pipeline/refresh_engine.py
```

**Frontend (Next.js)**
```bash
cd landing
npm install
npm run dev
```

Abre `http://localhost:3000` en el navegador.

## Despliegue

La landing page se hospeda en Firebase Hosting. Es un build estático de Next.js, así que simplemente:

```bash
cd landing
npm run build
firebase deploy
```

Antes de ir a producción, revisa [SECURITY.md](SECURITY.md) para el checklist de seguridad. Maneja los secretos en variables de entorno (`.env` local, o Secret Manager en GCP).

Si actualizas el pipeline Python, el próximo `refresh_engine.py` recalculará los scores. Los datos pueden vivir en Firestore o exportarse como CSV.

---

## Contribuir

Si quieres mejorar esto:

1. Lee [CONTRIBUTING.md](CONTRIBUTING.md) y [CLAUDE.md](CLAUDE.md) para estilo de código y convenciones.
2. Para el frontend (Next.js): respeta la paleta Midnight/Teal/Gold y usa variables CSS (no hardcodes de color).
3. Para el backend (Python): Pandas 3.0+ con Copy-on-Write, usa `config.py` para constantes.
4. Antes de hacer PR: `npm run build` en `landing/` y `pytest` en la raíz.

---

Gobernanza de Datos Abiertos NL 2026 — Una auditoría de calidad, con datos públicos y código público.
