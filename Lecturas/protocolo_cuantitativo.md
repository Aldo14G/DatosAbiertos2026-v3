# Protocolo de Investigación: Evaluación Automatizada de la Gobernanza de Datos Abiertos de Nuevo León 2026

## Capítulo 1: Introducción y Planteamiento del Problema

### 1.1 Antecedentes del Gobierno Abierto y los Datos Abiertos
La evolución de la administración pública hacia paradigmas de gobernanza interactiva ha consolidado al Gobierno Abierto (Open Government) como un eje rector para la legitimidad democrática. Dentro de esta doctrina, la apertura de datos gubernamentales, comúnmente referida bajo el acrónimo OGD (Open Government Data), constituye un pilar estratégico indispensable para garantizar la transparencia institucional, promover la rendición de cuentas, fomentar la colaboración ciudadana y habilitar la innovación pública basada en evidencia empírica. El modelo de datos abiertos asume que la publicación proactiva de la información producida por el Estado, en formatos legibles por máquinas y bajo licencias abiertas, empodera al ciudadano y genera un ecosistema de valor social y económico (Zuiderwijk, Janssen, & Davis, 2014).

Sin embargo, tras más de una década de iniciativas internacionales y nacionales orientadas a la publicación masiva de datos, la literatura académica especializada advierte que el simple acto de publicar conjuntos de datos (datasets) en la web no asegura, por sí mismo, su viabilidad técnica, ni mucho menos su aprovechamiento por parte de la sociedad (Batini, Cappiello, Francalanci, & Maurino, 2009). Diversos estudios han documentado la persistencia de una "brecha de usabilidad" derivada del deterioro en la calidad técnica de las bases de datos gubernamentales.

### 1.2 El Problema de la Calidad de los Datos Gubernamentales
Las deficiencias operativas crónicas presentes en los portales gubernamentales incluyen la proliferación de valores nulos (missing values), el uso de formatos propietarios o no estandarizados que dificultan el procesamiento automatizado, la ausencia de diccionarios de datos adecuados y, de manera crítica, el abandono sistémico de las frecuencias de actualización. Estas fallas no representan meros "errores de dedo", sino que constituyen fallas estructurales en los mecanismos de gobernanza de la información pública. Cuando un ciudadano, periodista, o científico de datos intenta utilizar los catálogos oficiales para alimentar modelos predictivos, investigaciones académicas o desarrollo de software, se enfrenta a un entorno de alta fricción técnica que a menudo vuelve inviable aprovechar el dato público.

En el contexto específico del Estado de Nuevo León, México, el portal oficial `catalogodatos.nl.gob.mx` ha aglutinado la información proporcionada por docenas de dependencias estatales utilizando el sistema de gestión de datos CKAN (Comprehensive Knowledge Archive Network). A pesar de contar con la infraestructura tecnológica subyacente para exponer conjuntos de datos, actualmente el ecosistema estatal carece de un instrumento automatizado, escalable y metódicamente fundamentado que permita auditar de forma sistémica y longitudinal la calidad de estos activos de información. Las revisiones de auditoría suelen recaer en evaluaciones formales manuales, sesgadas y episódicas, que ignoran la volumetría real y el nivel de cumplimiento normativo algorítmico.

Esta carencia metodológica y técnica imposibilita una evaluación objetiva. Si no existe un mecanismo central del que la administración pueda derivar inteligencia de calidad, resulta fácticamente imposible aplicar esquemas de mejora continua, limitando el descubrimiento de fallas estructurales en el ciclo de vida de los datos del Estado. 

### 1.3 Formulación del Problema
Con base en los antecedentes presentados, se argumenta que la adopción de infraestructuras analíticas de software, capaces de auditar y evaluar las dimensiones de completitud, exactitud, unicidad y consistencia bajo lineamientos internacionales formales, resulta fundamental para migrar de una etapa de publicación a una etapa de madurez en la gobernanza algorítmica.

Para abordar esta problemática empírica, el presente estudio formula la siguiente interrogante principal de investigación:

**¿En qué medida los conjuntos de datos publicados en el portal oficial `catalogodatos.nl.gob.mx` del Gobierno de Nuevo León cumplen con los estándares mínimos de calidad medibles (completitud, exactitud, consistencia temporal y unicidad) durante el año 2026?**

## Capítulo 2: Objetivos e Hipótesis de la Investigación

### 2.1 Objetivos Generales y Específicos
**Objetivo General:**
Diseñar, implementar algorítmicamente y desplegar un motor analítico automatizado que evalúe cuantitativamente la calidad de los datos del catálogo abierto del Estado de Nuevo León, aplicando de forma estricta el estándar normativo de la ISO/IEC 25012:2008 y los fundamentos del modelo de calidad de la información (Wang & Strong, 1996), para determinar el estado de la gobernanza de datos en el nivel subnacional.

**Objetivos Específicos:**
1. Desarrollar un protocolo de integración automatizada (*web scraper* y conector API) hacia el sistema CKAN para censar la totalidad del catálogo estatal sin intervención ni sesgos humanos.
2. Identificar el grado de completitud algorítimica de las tablas publicadas, calculando las tasas de valores nulos o vacíos.
3. Contrastar y cronometrar las frecuencias de actualización formales prometidas por las dependencias frente a las marcas de tiempo reales (*timestamps*) del servidor para diagnosticar la consistencia temporal.
4. Desarrollar un "Score Global de Gobernanza" dinámico escalable en un dashboard interactivo de visualización pública.

### 2.2 Hipótesis de Investigación

Sobre la base de exhaustivas revisiones teóricas y observaciones empíricas iniciales, se han elaborado supuestos probabilísticos sobre el fenómeno:

* **Hipótesis Principal ($H_1$):**
Los conjuntos de datos evaluados de forma directa y automatizada presentarán un *Score Global de Calidad* promedio estadísticamente inferior al 60% dentro de una escala normalizada de 0 a 100, lo que evidenciará deficiencias estructurales críticas en la metodología de su recolección y publicación.

* **Hipótesis Secundaria ($H_2$):**
De todas las dimensiones ISO 25012 operacionalizadas algorítmicamente, la métrica correspondiente a la *consistencia temporal* será la que decrete la menor puntuación promedio entre todas las entidades del Estado, reflejando el abandono sistemático en la manutención de los catálogos públicos mediante actualizaciones asíncronas.

## Capítulo 3: Marco Teórico y Conceptual

### 3.1 La Calidad de los Datos como Paradigma Dimensional
Para trascender las evaluaciones subjetivas o las auditorías manuales, la evaluación de un catálogo OGD exige que se determine formalmente qué constituye un "buen dato". El cuerpo literario fundamental comienza con el esquema desarrollado por Wang y Strong (1996). Para estos teóricos, la calidad informática dejó de ser una propiedad intrínseca y monolítica (basada meramente en la falta de errores). Argumentaron formalmente que la "calidad de los datos" (Data Quality o DQ) es una noción multidimensional dictada por la adecuación al uso ("fitness for use").

El marco de Wang y Strong segmenta la calidad de los datos en cuatro categorías teóricas que permean cualquier evaluación empírica moderna:
1. **DQ Intrínseca:** El dato guarda correlación estricta con la realidad que pretende representar (Exactitud, Objetividad).
2. **DQ de Contextualidad:** El dato sirve a las propensiones específicas del analista y está disponible temporalmente (Relevancia, Puntualidad).
3. **DQ Representacional:** El dato se presenta en un idioma interpretativo viable e interconectable (Intérprete uniforme, Consistencia representacional).
4. **DQ de Accesibilidad:** Las barreras a nivel seguridad y distribución web son viables (Accesibilidad y control perimetral).

### 3.2 Implementación Computacional y la Norma ISO/IEC 25012:2008
Ante la necesidad empírica de operativizar estos conceptos académicos en sistemas de ingeniería de software duros, surge la Organización Internacional de Normalización (ISO). El estándar **ISO/IEC 25012:2008** establece formalmente que el producto final de ciclo de desarrollo asume una "calidad de entidad representativa" de un fenómeno público (ISO/IEC, 2008). 

En el contexto estricto de este informe, el estándar fundamenta que la Gobernanza de Datos (variable latente) no puede ser evaluada por apreciación, sino a través del encadenamiento de métricas sistémicas observables generadas en las bases de datos de Nuevo León. La norma establece el marco evaluativo de "SQuaRE" (Software product Quality Requirements and Evaluation) proporcionando las directrices bajo las cuales se deben formular algoritmos prescriptivos para analizar datos sin necesidad de revisar su semántica visual o social. Bajo esta justificación epistemológica, el presente trabajo se soporta sobre ISO 25012 para argumentar que los algoritmos de completitud, precisión de formato y consistencia de actualización construyen efectivamente la realidad estadística de la gestión estatal.

## Capítulo 4: Metodología Cuantitativa de la Investigación

### 4.1 Enfoque, Paradigma y Nivel de Diseño
Siguiendo los lineamientos procedimentales de metodología avanzada, el estudio se inscribe en un enfoque científico empírico-analítico sustentado sobre un paradigma fuertemente positivista (Rojas Soriano, 2013). La metodología del presente protocolo es de clase cuantitativa porque recurre estrictamente a la medición algorítmica objetiva, recopilando matrices poblacionales de los metadatos y derivando inferencias fundamentadas en estadística descriptiva y distribucional (medias ponderadas, varianzas).

El nivel de diseño es de tipo **no experimental de corte transversal**, con un claro **alcance descriptivo y relacional exploratorio**. Se cataloga como no experimental ("ex post facto") dado que el investigador (el motor algorítmico `data_layer.py`) no incide, modifica, muta ni manipula las bases publicadas por el Gobierno de Nuevo León en su entorno natural; simple y rigurosamente se limita a observar, capturar y medir sus características sistémicas en un punto estático del tiempo. De manera congruente, el corte es transversal porque la recopilación automatizada se concreta durante un sub-periodo delimitado de 2026, lo cual ofrecerá una radiografía estadística unificada, sin ejecutar seguimiento a años o sexenios anteriores de forma comparada.

### 4.2 Población Universo y Delimitación Censal
Garantizar la validez interna de la métrica en la era cibernética exige definir la naturaleza algorítmica del acceso.
* **Población Universo:** La delimitación de la población objetivo la componen la totalidad geométrica de los recursos, dependencias y datasets que constituyen el portal público centralizado `catalogodatos.nl.gob.mx` vigente durante el año 2026.
* **Muestra Censal Automatizada:** A diferencia de las auditorías públicas típicas que operan sobre subconjuntos probabilísticos, el método cuantitativo aplicado en esta investigación ejecuta un **censo técnico absoluto**, eliminando totalmente el margen de error muestral. Utilizando integraciones de Python (PyArrow / Pandas DataFrame) y peticiones masivas iterativas hacia la Interfaz de Programación de Aplicaciones (API) de CKAN, el diseño examina matemáticamente todos los conjuntos publicados en la población, impidiendo el sesgo artificial de selección. 

* **Validación Cualitativa Paralela (n=30):** Aunque impera la óptica censal universal, la validación del instrumento tecnológico per se (el motor matemático de revisión de los scripts) requerirá una *muestra teórica de carácter intencional* equivalente a 30 *datasets* representativos, escogidos por saturación semántica. El algoritmo dictamina el estado de estos 30 elementos de prueba y los coteja contra escrutinio pericial humano, certificando la fidelidad del "Score Global de Calidad".

### 4.3 Operacionalización Algorítmica de las Variables
La fase principal del diseño subyace en cómo transitar de los conceptos axiomáticos expuestos por ISO/IEC a formulaciones ejecutables en código y evaluadas porcentualmente. Dicha operacionalización empírica es el pináculo de la matriz de investigación:

Para responder a $H_1$, la variable latente constructo (*Gobernanza General*) se formula computacionalmente como el **Score Global**, y este es directamente observable mediante las siguientes sub-dimensiones paramétricas:

1. **(C) Completitud [Pond: 30%]:** Definida como la extensión de campos presentes que no reportan valores inválidos y/o vacíos técnicos dentro del archivo JSON/CSV de origen. La fórmula matemática implícita extrae la resta de la población de celdas nulas entre el Universo de Celdas. Correlaciona matemáticamente la exactitud de captura.
2. **(A) Exactitud y Conformidad de Tipos (Accuracy) [Pond: 25%]:** Corresponde a la rigurosidad sintáctica subyacente. Se evalúa calculando la dispersión y la consistencia en el paradigma del cast de Pandas contra reglas semánticas RegEx. Determina si los IDs son de naturaleza numérica sin mutación, u fechas con formato estandarizado ISO 8601.
3. **(T) Consistencia Temporal (Timeliness) [Pond: 15%]:** Atiende a la variable de puntualidad cronológica. Operada matemáticamente tomando el diferencial entre el *metadata_modified* nativo del servidor contra la frecuencia declarada `frequency` en los diccionarios de metadatos. Esta métrica es fundamental en el estudio, constituyendo el punto a contrastar de la hipótesis $H_2$.
4. **(U) Unicidad Sistémica [Pond: 8%]:** Medición de colisiones algorítmicas, penalizando la existencia de registros primarios duplicados integralmente a nivel fila dentro de los sub-documentos procesados.
5. **(D) Factores de Documentación y Apertura Tecnológica [Pond: 17%]:** Operada según el sistema de 5 Estrellas de Tim Berners-Lee; penalizando repositorios con extensiones cerradas (e.g. PDF/DOCX) y otorgando las condecoraciones plenas a formatos expuestos en JSON/CSV.

### 4.4 Tratamiento Analítico, Software y Exposición
La recolección final del JSON validado a través del pipeline algorítmico alimenta una ingesta en bibliotecas de procesamiento en memoria (`PyArrow 23.0+`), posibilitando el análisis mediante estadística descriptiva. El flujo establece medidas de tendencia central global (medias, proporciones y desviaciones) categorizando todos los hallazgos en Clústeres de Comportamiento Jerárquico segmentado en Tiers de Calidad (e.g., Gobernanza Óptima si Score $\ge 90$; Peligro Operativo si Score $< 60$).

Finalmente, el resultado del experimento no recae meramente en el cuerpo del artículo o paper científico. El andamiaje teórico es reflejado algorítmicamente en tiempo real hacia una interfaz frontend (UI) diseñada explícitamente usando la arquitectura de `Streamlit 1.56+`, convirtiendo la instrumentación cualicuantitativa y los dashboards de KPIs estadísticos en infraestructura abierta al ciudadano bajo el marco del Sistema *Gobernanza Pro* de NL 2026.

---

## 5. Referencias (APA 7)

* Batini, C., Cappiello, C., Francalanci, C., & Maurino, A. (2009). Methodologies for data quality assessment and improvement. *ACM Computing Surveys (CSUR)*, 41(3), 1-52. https://doi.org/10.1145/1541880.1541883
* ISO/IEC. (2008). *ISO/IEC 25012:2008. Software engineering — Software product Quality Requirements and Evaluation (SQuaRE) — Data quality model*. International Organization for Standardization.
* Rojas Soriano, R. (2013). *Guía para realizar investigaciones sociales* (38.ª ed.). Plaza y Valdés.
* Wang, R. Y., & Strong, D. M. (1996). Beyond accuracy: What data quality means to data consumers. *Journal of Management Information Systems*, 12(4), 5-33. https://doi.org/10.1080/07421222.1996.11518099
* Zuiderwijk, A., Janssen, M., & Davis, C. (2014). Innovation with open data: Essential elements of open data ecosystems. *Information Polity*, 19(1, 2), 17-33. https://doi.org/10.3233/IP-140329
