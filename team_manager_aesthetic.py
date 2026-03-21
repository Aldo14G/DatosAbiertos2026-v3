import json, os, sys, datetime

TEAM_DIR = ".antigravity/team"
SHARED   = f"{TEAM_DIR}/shared"

TASKS_SPRINT2 = [
    # Agente Material Design
    {"id":1,  "title":"Leer quality_results y mapear rangos",      "agent":"agente_material", "deps":[]},
    {"id":2,  "title":"Mapear color roles M3 a paleta NL",         "agent":"agente_material", "deps":[1]},
    {"id":3,  "title":"Definir breakpoints semánticos de scores",   "agent":"agente_material", "deps":[2]},
    {"id":4,  "title":"Definir escala tipográfica Roboto",          "agent":"agente_material", "deps":[2]},
    {"id":5,  "title":"Escribir design_tokens.json",                "agent":"agente_material", "deps":[3,4]},
    # Agente Charts
    {"id":6,  "title":"Leer tokens y quality_results",             "agent":"agente_charts",   "deps":[5]},
    {"id":7,  "title":"FIX Bug #2: Heatmap ancho completo",        "agent":"agente_charts",   "deps":[6]},
    {"id":8,  "title":"FIX Bug #3: Eje X fechas reales",           "agent":"agente_charts",   "deps":[6]},
    {"id":9,  "title":"FIX Bug #1: KPI cards con color umbral",    "agent":"agente_charts",   "deps":[6]},
    {"id":10, "title":"Tooltips M3 en todas las gráficas",         "agent":"agente_charts",   "deps":[7,8]},
    {"id":11, "title":"Template Plotly universal con tokens",      "agent":"agente_charts",   "deps":[9,10]},
    {"id":12, "title":"Escribir components_registry.json",         "agent":"agente_charts",   "deps":[11]},
    # Agente Layout
    {"id":13, "title":"Leer tokens y components_registry",         "agent":"agente_layout",   "deps":[12]},
    {"id":14, "title":"CSS global M3 en st.markdown()",            "agent":"agente_layout",   "deps":[13]},
    {"id":15, "title":"Sidebar con navegación y metadata",         "agent":"agente_layout",   "deps":[14]},
    {"id":16, "title":"Sección 1: KPI cards M3",                   "agent":"agente_layout",   "deps":[14]},
    {"id":17, "title":"Sección 2: Heatmap en card M3",             "agent":"agente_layout",   "deps":[14]},
    {"id":18, "title":"Sección 3: Tabla con score color bars",     "agent":"agente_layout",   "deps":[14]},
    {"id":19, "title":"Sección 4: Alertas con badges severidad",   "agent":"agente_layout",   "deps":[14]},
    {"id":20, "title":"Sección 5: Evolución con anotaciones",      "agent":"agente_layout",   "deps":[14]},
    {"id":21, "title":"Footer con metadata del análisis",          "agent":"agente_layout",   "deps":[14]},
    {"id":22, "title":"Ensamblar dashboard_v2.py completo",        "agent":"agente_layout",   "deps":[15,16,17,18,19,20,21]},
]

def init_sprint2():
    for d in [f"{TEAM_DIR}/mailbox", f"{TEAM_DIR}/locks", SHARED]:
        os.makedirs(d, exist_ok=True)
    
    path = f"{TEAM_DIR}/tasks.json"
    data = {"proyecto": "Dashboard NL 2026 — Sprint 2: Aesthetic M3",
            "sprint": 2,
            "fecha_inicio": str(datetime.date.today()),
            "members": ["AldoGbot","agente_material","agente_charts","agente_layout"],
            "tasks": []}
    
    for t in TASKS_SPRINT2:
        data["tasks"].append({**t, "status":"PENDING", "plan_approved": False,
                              "created_at": str(datetime.datetime.now())})
    
    with open(path,"w", encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("✓ Sprint 2 inicializado — 22 tareas de mejora estética M3")
    print(f"  Agentes: agente_material → agente_charts → agente_layout")

def status():
    with open(f"{TEAM_DIR}/tasks.json", encoding='utf-8') as f: data = json.load(f)
    agents = {}
    for t in data["tasks"]:
        a = t["assigned_to"] if "assigned_to" in t else t.get("agent","?")
        agents.setdefault(a, {"done":0,"total":0})
        agents[a]["total"] += 1
        if t["status"] == "COMPLETED": agents[a]["done"] += 1
    
    print(f"\n{'='*55}")
    print(f"  Sprint 2: {data.get('proyecto','')}")
    print(f"{'='*55}")
    for agent, counts in agents.items():
        pct = counts["done"]/counts["total"]*100
        bar = "█" * int(pct/10) + "░" * (10-int(pct/10))
        print(f"  {agent:22} [{bar}] {counts['done']}/{counts['total']}")
    print(f"{'='*55}\n")

if __name__ == "__main__":
    cmds = {"init": init_sprint2, "status": status}
    if len(sys.argv) > 1 and sys.argv[1] in cmds:
        cmds[sys.argv[1]]()
    else:
        print("Uso: python team_manager_aesthetic.py [init|status]")
