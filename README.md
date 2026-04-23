# Gobernanza de Datos Abiertos Nuevo León 2026

![Estado](https://img.shields.io/badge/Estado-En_Desarrollo-amber)
![Python](https://img.shields.io/badge/Python-3.13+-blue)
![Next.js](https://img.shields.io/badge/Next.js-15.0+-black)

Plataforma automatizada para la auditoría y gobernanza de los datos abiertos del Gobierno del Estado de Nuevo León (`catalogodatos.nl.gob.mx`). Este proyecto evalúa conjuntos de datos (datasets) contra estándares internacionales de calidad de la industria (**ISO/IEC 25012:2008**, **ISO 8000** y **DAMA-DMBOK**) y proporciona dos interfaces de alto rendimiento: un *Dashboard Analítico en Streamlit* y una *Landing Page Premium en Next.js*.

## 🌟 Arquitectura del Proyecto

El ecosistema se compone de dos frentes tecnológicos:

1. **Pipeline de Datos & Dashboard (Python / Streamlit)**
   - **Motor ETL:** Extrae metadatos y recursos del API de CKAN.
   - **Motor de Scoring:** Audita las 5 dimensiones de calidad de datos.
   - **Dashboard (Streamlit):** Visualización interactiva para analistas, con un sistema de diseño inyectado vía CSS (Material Design 3 / Stitch).
   - *Ubicación:* Carpeta raíz (`dashboard_v3.py`, `pipeline/`, `sections/`).

2. **Plataforma Pública (Next.js 15 / React / Tailwind)**
   - Landing page moderna que expone el ranking y la metodología al público.
   - Desarrollada con componentes de interfaz premium (*Glassmorphism*, paleta *Midnight/Teal/Gold*).
   - Componentes interactivos como `PremiumFeatureTabs`.
   - *Ubicación:* Carpeta `landing/`.

## 📐 Estándar de Evaluación (ISO/IEC 25012:2008)

El algoritmo de calidad penaliza o premia los datasets en base a las siguientes dimensiones:
- **Completitud (30%):** Ausencia de valores nulos o celdas vacías críticas.
- **Oportunidad (25%):** Frecuencia de actualización y frescura del dato.
- **Accesibilidad (20%):** Enlaces rotos (HTTP 404), APIs disponibles.
- **Documentación (15%):** Diccionarios de datos, descripciones detalladas.
- **Apertura (10%):** Formatos estructurados y abiertos (CSV, JSON vs PDF).

Los datasets se agrupan en tres niveles (*Tiers*):
- 🥇 **Gold (≥ 90 pts):** Datos óptimos.
- 🥈 **Silver (70–89 pts):** Accesibles pero con áreas de mejora.
- 🥉 **Bronze (< 70 pts):** Requieren remediación inmediata.

## 🚀 Guía de Inicio Rápido (Quick Start)

### 1. Iniciar el Dashboard Analítico (Python)
Requiere Python 3.13+.

```bash
# Instalar dependencias base y de desarrollo
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Correr el dashboard en Streamlit
streamlit run dashboard_v3.py
```

### 2. Iniciar la Plataforma Pública (Next.js)
Requiere Node.js 20+.

```bash
# Navegar a la carpeta frontend
cd landing

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```
La aplicación estará disponible en `http://localhost:3000`.

## ☁️ Despliegue en la Nube
El proyecto está configurado para desplegarse ágilmente en **Google Cloud Run**. Se recomienda utilizar un archivo ZIP ligero omitiendo carpetas pesadas (`.venv`, `node_modules`, `.git`) para evitar cuellos de botella del *Cloud Build*.

## 🤝 Contribuir al Proyecto
Si deseas mejorar el código, crear nuevos componentes o ajustar la lógica de las métricas, por favor revisa el archivo [CONTRIBUTING.md](CONTRIBUTING.md). Encontrarás las guías de estilo, el uso estricto de la paleta *Midnight/Teal/Gold*, y las instrucciones para el ecosistema multi-agente (AI).

---
*Datos Abiertos NL 2026 - Gobernanza y Transparencia.*
