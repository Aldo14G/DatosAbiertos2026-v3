# Calidad Pro: Framework Avanzado de Gobernanza (Agentes de Datos)

El pipeline de extracción y validación de Datos Abiertos para **Nuevo León 2026** no solo utiliza métricas básicas, sino que adopta una arquitectura completa de roles ("Agentes") estructurada en dos motores principales para garantizar cobertura real de normativas de gobernanza.

Este submódulo se detona mediante:
```bash
python pipeline/refresh_engine.py --advanced
```
Esto creará el archivo `.antigravity/team/shared/advanced_quality_results.json` que la vista del Dashboard consumirá.

## Arquitectura de Módulos (Agentes)

### 1. Extractor (Skill 1)
Responsable de conectarse a la API de CKAN (u otra detectada dinámicamente) y realizar extracciones físicas profundas saltándose barreras de limitadores.
- Descubre todos los paquetes existentes.
- Utiliza **chardet** y **pandoc** intermedio para parsear bases de datos dañadas, corrigiendo encodings (`ISO-8859-1`, `UTF-8-SIG`, `CP1252`).
- Consolida recursos en CSV, JSON, GeoJSON y Excel a *Dataframes vectorizados*.

### 2. Evaluador (Skill 2)
Capa multiprisma. Cruza cada dataframe extraído contra 3 libros de estándares distintos en tiempo real.

#### A. Analizador ISO/IEC 25012:2008 (Calidad del Producto de Software - Datos)
- **Completitud**: Castiga fuertemente variables subyacentes con exceso de nulos `NaN`.
- **Exactitud**: Comprueba expresiones regulares a nivel celular (Fechas incorrectas, formato curvado, teléfonos rotos).

#### B. Analizador ISO 8000 (Calidad de Datos Maestros)
- **Unicidad**: Escaneo vectorizado de duplicados y penalización por ruido sintáctico.
- **Trazabilidad**: Certifica orígenes para linaje y metadatos complementarios en las llaves del JSON de CKAN.

#### C. Analizador DAMA-DMBOK 2.0 (Cuerpo de Conocimiento de Gestión de Datos)
- **Interoperabilidad Geográfica**: Si se detecta un catálogo de alcance generalizado con terminología de ubicaciones (ejemplo: Monterrey, San Nicolás), exige para alcanzar 100% que tenga las llaves cruzadas formales `cve_ent` (Entidad) y `cve_mun` (Municipio). Si estas variables no existen, se restan 20 puntos por falta de arquitectura de datos moderna.

> El tablero en su versión final leerá todos estos hallazgos consolidándolos en métricas legibles, una matriz de error por severidad (Crítico, Medio, Informativo) y un gráfico de cajas.
