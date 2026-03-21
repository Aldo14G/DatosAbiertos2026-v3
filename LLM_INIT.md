# 🤖 ARCHIVO DE INICIALIZACIÓN PARA LLMs (LLM_INIT)
**PROYECTO:** Gobernanza de Datos Abiertos Nuevo León 2026 (Open Data Quality Analyzer NL 2026)  
**CONTEXTO DE SISTEMA:** Este documento debe ser leído primero por cualquier LLM o Agente de IA para comprender holísticamente el propósito, la arquitectura de carpetas y los métodos de este repositorio.

---

## 1. RESUMEN DEL PROYECTO
Este repositorio aloja la infraestructura de un motor cuantitativo y un dashboard analítico para auditar la **Calidad de los Datos Abiertos Gubernamentales de Nuevo León (`catalogodatos.nl.gob.mx`)**.  

El proyecto tiene dos facetas fundamentales:
1. **La Técnica:** Consiste en un pipeline en Python que ingesta metadatos y los evalúa contra 4 dimensiones de calidad estandarizadas (Completitud, Exactitud, Unicidad, Consistencia). El frontend está construido en Streamlit, pero anula sus estilos por defecto para utilizar un diseño *pixel-perfect* de **Google Stitch (Material Design 3)** inyectado a través de HTML/CSS.
2. **La Metodológica / Académica:** El 100% del ecosistema está fundamentado en rúbricas de investigación científica social. El proyecto evoluciona el experimento "Cómo vamos en Datos" (LabNL, 2024), donde se utilizaban piezas LEGO para entender la precisión de los datos. En esta versión 2026, esos constructos de LEGO fueron codificados matemáticamente en nuestra herramienta como métricas algorítmicas de gobernanza.

---

## 2. MAPA DEL REPOSITORIO Y ARQUITECTURA

### 📁 `.antigravity/` y 📁 `.gemini/`
* (Archivos de infraestructura de agentes IA. Puedes ignorarlos para el análisis funcional del código).

### 📁 `sections/` (Módulos del Dashboard Streamlit)
El UI fue refactorizado usando inyecciones crudas HTML (`st.markdown(unsafe_allow_html=True)`) para replicar mocks de Stitch M3. Ningún componente nativo de Streamlit debe romper la jerarquía de las CSS variables.
* `resumen.py`: Tarjetas KPI y barra de distribución de puntajes globales.
* `categorias.py`: Tabla HTML que renderiza un Heatmap (semáforo de impacto) por categorías gubernamentales.
* `datasets.py`: Explorador interactivo con `st.dataframe` y barras de progreso (`column_config`).
* `alertas.py`: Tarjetas de fallas críticas (Score < 70) recomendando acciones a los enlaces de gobernanza.
* `evolucion.py`: Uso de `plotly.graph_objects` simulando curvas SVG nativas transparentes.
* `avanzado.py`: Renderizado duro de circunferencias (SVG Gauges) y Matrices de Correlación Heatmap.

### 📁 `styles/`
* `global_css.py`: **El núcleo del diseño**. Contiene el CSS (`inject_stitch_design_system()`) con las tokens absolutas extraídas de Tailwind/Stitch. Controla el NavBar, SideBar estilo *pill*, y todas las clases globales (`.kpi-card`, `.category-badge`).

### 📁 `stitch_screens/` y 📁 `stitch_output/`
* Contienen los `.html` exportados puros de Google Stitch (Modo Dark y Light). Son la "fuente de verdad" del diseño de la cual el módulo `styles` extrae las propiedades para Streamlit.

### 📄 Archivos Raíz (Core)
* `dashboard_v3.py`: El archivo de orquestación principal (Ejecutable con `streamlit run dashboard_v3.py`). Ensambla la UI llamando a los módulos de `sections/` e inyectando `styles/global_css.py`.
* `data_layer.py`: Capa de ingestión. Funciones de limpieza y filtrado de datasets.
* `/brain/.../protocolo_investigacion.md`: *Ubicado en la memoria de antigravity*. Plan de validación académica redactado en tiempo futuro para docentes. Define las variables y el enfoque cuantitativo de investigación.
* `/brain/.../documentacion_academica.md`: Justificación teórica (Wang & Strong, ISO 25012) para que el LLM pueda generar *papers* científicos.

---

## 3. INSTRUCCIONES PARA AGENTES DE IA (System Prompt)
Cuando ayudes al desarrollador "Aldo" (Aldo14G) en este repositorio, DEBES seguir estas reglas:
1. **NUNCA rompas el diseño:** Si Aldo te pide agregar un componente al dashboard, NO uses primitivos genéricos como `st.metric()` o `st.success()`. Debes crear el bloque HTML replicando la paleta Material 3 definida en `global_css.py`.
2. **Postura Académica:** Si se te pide escribir, asume una postura analítica y positivista sustentada en variables empíricas (Rojas Soriano). Evalúas la calidad del dato enfocándote en *Completitud, Exactitud, Unicidad y Consistencia*.
3. **No Caches:** No uses `@st.cache_resource` para el estilo o UI principal mientras Aldo esté depurando (a menos que se pida expresamente).
4. **Respeto a Streamlit:** Asegúrate de entender que estamos engañando a Streamlit para que parezca una Single Page Application moderna. `dashboard_v3.py` se encarga de rutar las opciones del menú lateral (`nav`) importando los ejecutables en `/sections/`.

---
*Fin del archivo de contexto.* Mantenlo en memoria para toda modificación transversal del repositorio.
