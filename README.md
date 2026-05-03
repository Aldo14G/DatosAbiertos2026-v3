# Gobernanza de Datos Abiertos Nuevo León 2026

![Estado](https://img.shields.io/badge/Estado-Producci%C3%B3n-success)
![Python](https://img.shields.io/badge/Python-3.13+-blue)
![Next.js](https://img.shields.io/badge/Next.js-15.0+-black)

Plataforma automatizada para la auditoría y gobernanza de los datos abiertos del Gobierno del Estado de Nuevo León (`catalogodatos.nl.gob.mx`). Este proyecto evalúa conjuntos de datos (datasets) contra estándares internacionales de calidad de la industria (**ISO/IEC 25012:2008**, **ISO 8000** y **DAMA-DMBOK**) y proporciona dos interfaces de alto rendimiento: un *Dashboard Analítico en Streamlit* (backend de evaluación) y una *Landing Page Premium en Next.js* (frontend público).

---

## 🌟 Arquitectura del Proyecto

El ecosistema se compone de dos frentes tecnológicos, manteniendo una estricta separación de responsabilidades y un orden jerárquico limpio:

1. **Pipeline de Datos & Dashboard (Python / Streamlit)**
   - **Motor ETL:** Extrae metadatos y recursos del API de CKAN de Nuevo León (`pipeline/fetcher.py`).
   - **Motor de Scoring:** Audita las 5 dimensiones de calidad de datos (`data_layer.py`).
   - **Dashboard Interno:** Visualización interactiva para analistas, con un sistema de diseño inyectado vía CSS (Material Design 3 / Stitch).
   - *Ubicación:* Carpeta raíz (`dashboard_v3.py`, `pipeline/`, `sections/`).

2. **Plataforma Pública Web (Next.js 15 / React / Tailwind)**
   - Landing page moderna que expone el ranking y la metodología al público.
   - Desarrollada con componentes de interfaz premium (*Glassmorphism*, paleta *Midnight/Teal/Gold*), componentes de Shadcn UI y animaciones con Framer Motion.
   - *Ubicación:* Carpeta `landing/`.

3. **Documentación técnica (`docs/`)**
   - Especificaciones de diseño, decisiones de producto, auditoría de calidad y guías de contribución.
   - Para despliegue y postura de seguridad, ver [DEPLOYMENT.md](DEPLOYMENT.md) y [SECURITY.md](SECURITY.md).

---

## 📐 Estándar de Evaluación (ISO/IEC 25012:2008)

El algoritmo de calidad penaliza o premia los datasets en base a las siguientes dimensiones:
- **Completitud (30%):** Ausencia de valores nulos o celdas vacías críticas.
- **Oportunidad (25%):** Frecuencia de actualización y frescura del dato.
- **Accesibilidad (20%):** Enlaces rotos (HTTP 404), APIs disponibles.
- **Documentación (15%):** Diccionarios de datos, descripciones detalladas.
- **Apertura (10%):** Formatos estructurados y abiertos (CSV, JSON vs PDF).

Los datasets se agrupan en tres niveles de salud de datos (*Tiers*):
- 🥇 **Gold (≥ 90 pts):** Datos óptimos y altamente confiables.
- 🥈 **Silver (70–89 pts):** Accesibles pero con áreas de mejora técnica.
- 🥉 **Bronze (< 70 pts):** Requieren remediación inmediata por parte de la dependencia.

---

## 🚀 Guía de Instalación y Ejecución (Paso a Paso)

Si deseas clonar, mejorar o auditar este proyecto, sigue estos pasos cuidadosamente:

### Pre-requisitos
- **Python 3.13+** (Para el motor de datos)
- **Node.js 20+** (Para la interfaz web pública)
- **Git**

### Paso 1: Clonar el Repositorio
```bash
git clone https://github.com/Aldo14G/DatosAbiertos2026-v3.git
cd DatosAbiertos2026-v3
```

### Paso 2: Configurar y Correr el Backend de Datos (Python)
Este entorno ejecuta las evaluaciones de calidad y levanta el dashboard interno.

```bash
# 1. Crear y activar entorno virtual (Opcional pero recomendado)
python -m venv .venv
source .venv/Scripts/activate # En Windows
# source .venv/bin/activate   # En Mac/Linux

# 2. Instalar dependencias base y de desarrollo
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 3. Extraer y evaluar datos (Actualiza el modelo de scoring local)
python pipeline/refresh_engine.py

# 4. Correr el dashboard analítico en Streamlit
streamlit run dashboard_v3.py
```
> El dashboard estará disponible en `http://localhost:8501`.

### Paso 3: Iniciar la Plataforma Pública (Next.js)
Este entorno levanta la página web moderna orientada a la ciudadanía.

```bash
# 1. Navegar a la carpeta frontend
cd landing

# 2. Instalar dependencias de Node
npm install

# 3. Iniciar el servidor de desarrollo
npm run dev
```
> La web pública estará disponible en `http://localhost:3000`.

---

## ☁️ Despliegue en producción

Arquitectura híbrida:

- **Landing pública (Next.js)** → Firebase App Hosting
- **Dashboard analítico (Streamlit)** → Cloud Run, expuesto vía rewrite de
  Firebase Hosting para servirse desde el mismo dominio

El procedimiento completo (incluyendo creación del proyecto GCP, Secret
Manager, despliegue desde fuente, dominio personalizado, CI/CD con
Workload Identity Federation y rollback) está en
**[DEPLOYMENT.md](DEPLOYMENT.md)**.

> ⚠️ **Antes de exponer el servicio al público**, completa el checklist
> de seguridad de **[SECURITY.md](SECURITY.md)** (manejo de secretos,
> rate limiting, alertas de costo, rotación de credenciales).

Variables de entorno: copia [`.env.example`](.env.example) a `.env` y
ajusta valores. En producción, los secretos viven en Google Secret
Manager — nunca en archivos.

Imagen Docker: el [`Dockerfile`](Dockerfile) está optimizado para Cloud
Run (usuario no-root, healthcheck, XSRF habilitado, telemetría
deshabilitada).

---

## 🤝 ¿Cómo Contribuir o Mejorar el Proyecto?

El repositorio ha sido optimizado y limpiado para dejar únicamente los módulos críticos. Si deseas contribuir:

1. Lee detenidamente el archivo [CONTRIBUTING.md](CONTRIBUTING.md) y [CLAUDE.md](CLAUDE.md). Encontrarás las guías de estilo rigurosas y el uso estricto de la paleta *Midnight/Teal/Gold*.
2. Asegúrate de que cualquier nuevo componente web siga la filosofía *Glassmorphism* y respete las variables CSS.
3. Para la capa de datos, se asume el uso de **Pandas 3.0+ con Copy-on-Write** (minimiza mutaciones en el lugar).
4. Crea tu propia rama funcional, valida que tus cambios no rompen el build (`npm run build` en landing y `pytest` en la raíz) y levanta un Pull Request.

---
*Gobernanza de Datos Abiertos NL 2026 — Transparencia, Calidad y Rigor Analítico.*
