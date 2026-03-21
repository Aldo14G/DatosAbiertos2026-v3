<h1 align="center">
  Gobernanza de Datos Abiertos Nuevo León 2026
</h1>

<p align="center">
  <i>Infraestructura automatizada para la calidad y auditoría de conjuntos de datos gubernamentales.</i>
</p>

---

## 📌 Contexto del Proyecto

La apertura pasiva de datos en portales gubernamentales no asegura su valor público. Múltiples estudios han detectado silos de información, problemas de estructura y desactualizaciones crónicas. Este proyecto evoluciona la iniciativa **¿Cómo vamos en Datos en Nuevo León? (2024, LabNL)**, transitando desde un enfoque educativo (con ladrillos LEGO) hacia una plataforma cuantitativa robusta y estandarizada.

La herramienta descarga, procesa y audita los repositorios públicos de [catalogodatos.nl.gob.mx](https://catalogodatos.nl.gob.mx) utilizando un modelo estadístico de validación apoyado en la norma **ISO/IEC 25012:2008**.

### Módulos Analíticos de Evaluación:
- **Completitud:** Campos obligatorios vs. nulos y esquemas estandarizados.
- **Exactitud:** Variables *machine-readable* y tipificación correcta.
- **Consistencia temporal:** Frecuencias de publicación nominales vs. latencias reales.
- **Unicidad:** Validación de claves primarias e índices duplicados.

---

## 🖥️ Arquitectura y Tecnologías
La plataforma está sustentada por un Pipeline algorítmico y una capa de Front-End reconstruida en Python para proporcionar un entorno *pixel-perfect* de UI/UX ejecutiva:

* **Engine Core:** `Python 3.10+`, `Pandas`, Scripts determinísticos de gobernanza.
* **Interfaz Visual:** `Streamlit`, pero **sobrescrita íntegramente** en CSS (`st.markdown`) simulando los *tokens* atómicos y directrices de diseño del sistema **Google Material Design 3 (M3) vía Google Stitch**.
* **Integración AI:** Componentes de LLM (`agente_dashboard.py` / Gemini) para revisión semántica y apoyo a la clasificación de anomalías complejas.
* **Visualización Dinámica:** Plotly (Áreas rellenadas a eje y, Gauges de SVG en crudo).

---

## 📂 Organización del Repositorio
```
📦 DatosAbiertos2026
 ┣ 📂 sections/          # Vistas (Resumen, Explorador, Heatmaps, Alertas, Avanzado)
 ┣ 📂 styles/            # Sistema global CSS inyectado (Simulador de Google Stitch)
 ┣ 📂 stitch_screens/    # Mocks HTML de referencia UI (Fuente de Verdad de diseño)
 ┣ 📄 dashboard_v3.py    # Main Orquestador del Dashboard (El archivo ejecutable)
 ┣ 📄 data_layer.py      # Filtros, limpiezas e Ingesta de Datos (ETL básico)
 ┣ 📄 LLM_INIT.md        # Documento inicial de contexto System Prompt para Agentes IA
 ┗ 📄 README.md          # Este archivo
```

---

## 🚀 Despliegue e Instalación
El proyecto se ejecuta en local mediante el entorno Streamlit de manera asíncrona:

1. Clona el repositorio:
   ```bash
   git clone https://github.com/Aldo14G/open-data-quality-nl-2026.git
   cd open-data-quality-nl-2026
   ```

2. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Monta el servidor del Dashboard:
   ```bash
   streamlit run dashboard_v3.py
   ```
El sistema debe estar expuesto localmente en `http://localhost:8501`.

---

## 📑 Soporte Académico y Metodológico
Este repositorio está documentado de principio a fin utilizando el rigor de los constructos nomológicos de Mendoza Gómez y los diseños empíricos propuestos por Rojas Soriano. El motor computacional funge formalmente como la **herramienta de medición** del Protocolo Institucional.

> **Licencia:** MIT | Creado por [Aldo14G](https://github.com/Aldo14G)
