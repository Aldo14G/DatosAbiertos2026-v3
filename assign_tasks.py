import team_manager

tasks = [
    ("Descubrir todos los datasets via API CKAN /api/3/action/package_search", "agente_investigador", []),
    ("Registrar metadatos: categoría, organización, formato, fecha de última modificación, URL de descarga", "agente_investigador", [1]),
    ("Detectar datasets nuevos vs. los existentes en el repo de referencia (diff 2024 → 2026)", "agente_investigador", [1]),
    ("Verificar accesibilidad de cada URL de descarga (HTTP 200 vs. errores)", "agente_investigador", [2]),
    ("Escribir portal_snapshot_2026.json y datasets_index.json en shared/", "agente_investigador", [3, 4]),
    ("Notificar a AldoGbot con resumen: N datasets activos, N con URL rota, N categorías", "agente_investigador", [5]),
    ("Leer datasets_index.json y filtrar solo recursos CSV accesibles", "agente_codigo", [5]),
    ("Descargar todos los CSV con manejo de codificaciones (UTF-8, Latin-1, CP1252)", "agente_codigo", [7]),
    ("Ejecutar análisis de Completeness -> % completitud global y por columna", "agente_codigo", [8]),
    ("Ejecutar análisis de Accuracy -> score penalizado por tipos mixtos y errores de formato", "agente_codigo", [8]),
    ("Ejecutar análisis de Consistency -> % outliers IQR + inconsistencias de capitalización", "agente_codigo", [8]),
    ("Ejecutar análisis de Uniqueness -> % duplicados exactos + cardinalidad media", "agente_codigo", [8]),
    ("Calcular score global (promedio de 4 dimensiones) por dataset", "agente_codigo", [9, 10, 11, 12]),
    ("Escribir quality_results.json en shared/ con schema acordado por AldoGbot", "agente_codigo", [13]),
    ("Notificar a AldoGbot: análisis completo, N datasets procesados, N fallidos", "agente_codigo", [14]),
    ("Leer quality_results.json y validar schema antes de construir", "agente_dashboard", [14]),
    ("Diseñar estructura del dashboard: layout, secciones, filtros", "agente_dashboard", [16]),
    ("Construir vista Resumen del Portal: KPIs globales", "agente_dashboard", [17]),
    ("Construir vista Por Categoría: heatmap 4 dimensiones x 16 categorías", "agente_dashboard", [17]),
    ("Construir vista Por Dataset: tabla interactiva con búsqueda y filtros", "agente_dashboard", [17]),
    ("Construir vista Alertas: datasets con score global < 70% listados como prioritarios", "agente_dashboard", [17]),
    ("Construir vista Evolución 2024 -> 2026: comparativa si el repo tiene datos históricos", "agente_dashboard", [17]),
    ("Empaquetar dashboard: requirements.txt + instrucciones de ejecución local y Colab", "agente_dashboard", [18, 19, 20, 21, 22]),
    ("Notificar a AldoGbot: dashboard listo, rutas de archivos, instrucciones de uso", "agente_dashboard", [23])
]

for i, (title, assigned_to, deps) in enumerate(tasks):
    team_manager.assign_task(title, assigned_to, deps, task_id=i+1)
