import json, os, sys, datetime

TEAM_DIR = ".antigravity/team"

TASKS_SPRINT3 = [
    # Agente Normalizer — va PRIMERO
    {"id":1,  "title":"Detectar categorías duplicadas en JSON",     "agent":"agente_normalizer","deps":[]},
    {"id":2,  "title":"Crear mapa de normalización str.title()",    "agent":"agente_normalizer","deps":[1]},
    {"id":3,  "title":"Aplicar normalización y sobrescribir JSON",  "agent":"agente_normalizer","deps":[2]},
    {"id":4,  "title":"Añadir RdYlGn a design_tokens.json",         "agent":"agente_normalizer","deps":[1]},
    {"id":5,  "title":"Notificar a AldoGbot: diff categorías",      "agent":"agente_normalizer","deps":[3,4]},
    # Agente Heatmap — inicia solo cuando T5 COMPLETED
    {"id":6,  "title":"Reconstruir heatmap con RdYlGn",             "agent":"agente_heatmap",  "deps":[5]},
    {"id":7,  "title":"Añadir anotaciones numéricas en celdas",     "agent":"agente_heatmap",  "deps":[6]},
    {"id":8,  "title":"Tooltips con dimensiones por hover",         "agent":"agente_heatmap",  "deps":[6]},
    {"id":9,  "title":"Línea de referencia score medio portal",     "agent":"agente_heatmap",  "deps":[6]},
    {"id":10, "title":"Validar: 16 categorías, no duplicados",      "agent":"agente_heatmap",  "deps":[7,8,9]},
    # Agente KPI (paralelo con heatmap desde T5)
    {"id":11, "title":"KPI cards con ícono + barra de progreso",    "agent":"agente_kpi",      "deps":[5]},
    {"id":12, "title":"Segunda fila KPIs: Exactitud + Mejor DS",    "agent":"agente_kpi",      "deps":[11]},
    {"id":13, "title":"Alerta cards con 4 dimensiones por DS",      "agent":"agente_kpi",      "deps":[5]},
    {"id":14, "title":"Link 'Ver en portal →' por cada alerta",     "agent":"agente_kpi",      "deps":[13]},
    # Agente Viz (paralelo con heatmap desde T5)
    {"id":15, "title":"Radar chart 4 dimensiones del portal",       "agent":"agente_viz",      "deps":[5]},
    {"id":16, "title":"Histograma distribución de scores",          "agent":"agente_viz",      "deps":[5]},
    {"id":17, "title":"Barras Top10 mejor + Top10 peor datasets",   "agent":"agente_viz",      "deps":[5]},
    {"id":18, "title":"Integrar 4 gráficas en st.tabs()",           "agent":"agente_viz",      "deps":[15,16,17]},
    # Integración final (AldoGbot)
    {"id":19, "title":"QA visual: heatmap correcto (16 cats, RdYlGn)","agent":"AldoGbot",      "deps":[10]},
    {"id":20, "title":"QA KPIs: barras de progreso visibles",       "agent":"AldoGbot",        "deps":[12,14]},
    {"id":21, "title":"QA Tabs sección 5: 4 pestañas funcionales",  "agent":"AldoGbot",        "deps":[18]},
    {"id":22, "title":"Merge dashboard_v3.py + broadcast cierre",   "agent":"AldoGbot",        "deps":[19,20,21]},
]

def init_sprint3():
    os.makedirs(f"{TEAM_DIR}/mailbox", exist_ok=True)
    os.makedirs(f"{TEAM_DIR}/locks",   exist_ok=True)

    path = f"{TEAM_DIR}/tasks.json"
    data = {
        "proyecto": "Dashboard NL 2026 — Sprint 3: Precision Fixes + New Viz",
        "sprint": 3,
        "fecha_inicio": str(datetime.date.today()),
        "members": ["AldoGbot","agente_normalizer","agente_heatmap","agente_kpi","agente_viz"],
        "tasks": []
    }
    for t in TASKS_SPRINT3:
        data["tasks"].append({**t, "status":"PENDING", "plan_approved": False, "created_at": str(datetime.datetime.now())})
        
    with open(path,"w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✓ Sprint 3 inicializado — 22 tareas")
    print()
    print("  ORDEN DE EJECUCIÓN:")
    print("  1. agente_normalizer (T1-T5) → BLOQUEANTE para todos")
    print("  2. agente_heatmap (T6-T10)   → en serie")
    print("  2. agente_kpi (T11-T14)      → en paralelo con heatmap")
    print("  2. agente_viz (T15-T18)      → en paralelo con heatmap")
    print("  3. AldoGbot QA (T19-T22)     → cierre del sprint")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        init_sprint3()
    elif len(sys.argv) > 1 and sys.argv[1] == "status":
        import team_manager
        team_manager.print_status()
