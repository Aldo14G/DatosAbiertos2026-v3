import json, os, sys, datetime

TEAM_DIR  = ".antigravity/team"
SHARED    = f"{TEAM_DIR}/shared"

def init_team():
    """Inicializa la infraestructura del equipo para el proyecto NL 2026."""
    for d in [f"{TEAM_DIR}/mailbox", f"{TEAM_DIR}/locks", SHARED]:
        os.makedirs(d, exist_ok=True)

    tasks_path = f"{TEAM_DIR}/tasks.json"
    if not os.path.exists(tasks_path):
        tareas_iniciales = {
            "proyecto": "Calidad Datos Abiertos NL 2026",
            "repo": "github.com/Aldo14G/Calidad-de-Datos-Abiertos-en-Nuevo-Leon-2026",
            "fecha_inicio": str(datetime.date.today()),
            "tasks": [],
            "members": [
                "AldoGbot",
                "agente_investigador",
                "agente_codigo",
                "agente_dashboard"
            ]
        }
        with open(tasks_path, "w") as f:
            json.dump(tareas_iniciales, f, indent=2, ensure_ascii=False)

    for fname in ["broadcast.msg", "shared/datasets_index.json",
                  "shared/portal_snapshot_2026.json", "shared/quality_results.json"]:
        fpath = f"{TEAM_DIR}/{fname}"
        if not os.path.exists(fpath):
            with open(fpath, "w") as f:
                f.write("{}" if fname.endswith(".json") else "")

    print("✓ Equipo AldoGbot — Proyecto NL 2026 inicializado.")
    print(f"  Directorio: {TEAM_DIR}/")

def assign_task(title, assigned_to, deps=[], task_id=None):
    path = f"{TEAM_DIR}/tasks.json"
    with open(path, "r+", encoding='utf-8') as f:
        data = json.load(f)
        tid = task_id or len(data["tasks"]) + 1
        task = {
            "id": tid,
            "title": title,
            "status": "PENDING",
            "plan_approved": False,
            "assigned_to": assigned_to,
            "dependencies": deps,
            "created_at": str(datetime.datetime.now())
        }
        data["tasks"].append(task)
        f.seek(0); json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✓ T{tid} [{assigned_to}]: {title}")

def approve_plan(task_id):
    path = f"{TEAM_DIR}/tasks.json"
    with open(path, "r+", encoding='utf-8') as f:
        data = json.load(f)
        for t in data["tasks"]:
            if t["id"] == task_id:
                t["plan_approved"] = True
                t["status"] = "IN_PROGRESS"
        f.seek(0)
        f.truncate()
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✓ AldoGbot aprobó plan de T{task_id} — estado: IN_PROGRESS")

def complete_task(task_id):
    path = f"{TEAM_DIR}/tasks.json"
    with open(path, "r+", encoding='utf-8') as f:
        data = json.load(f)
        for t in data["tasks"]:
            if t["id"] == task_id:
                t["status"] = "COMPLETED"
                t["completed_at"] = str(datetime.datetime.now())
        f.seek(0)
        f.truncate()
        json.dump(data, f, indent=2, ensure_ascii=False)
    # Liberar lock si existe
    lock = f"{TEAM_DIR}/locks/task_{task_id}.lock"
    if os.path.exists(lock): os.remove(lock)
    print(f"✓ T{task_id} COMPLETED. Lock liberado.")

def broadcast(sender, text):
    msg = {"de": sender, "tipo": "BROADCAST",
           "ts": str(datetime.datetime.now()), "mensaje": text}
    with open(f"{TEAM_DIR}/broadcast.msg", "a", encoding='utf-8') as f:
        f.write(json.dumps(msg, ensure_ascii=False) + "\n")
    print(f"✓ BROADCAST de {sender}: {text[:60]}...")

def send_message(sender, receiver, text):
    msg = {"de": sender, "ts": str(datetime.datetime.now()), "mensaje": text}
    with open(f"{TEAM_DIR}/mailbox/{receiver}.msg", "a", encoding='utf-8') as f:
        f.write(json.dumps(msg, ensure_ascii=False) + "\n")
    print(f"✓ MSG {sender} → {receiver}: {text[:60]}...")

def status():
    path = f"{TEAM_DIR}/tasks.json"
    with open(path, encoding='utf-8') as f: data = json.load(f)
    print(f"\n{'='*55}")
    print(f"  Proyecto: {data.get('proyecto','')}")
    print(f"  Inicio  : {data.get('fecha_inicio','')}")
    print(f"{'='*55}")
    for t in data.get("tasks", []):
        icon = {"PENDING":"⏳","IN_PROGRESS":"🔄","COMPLETED":"✅"}.get(t["status"],"❓")
        print(f"  {icon} T{t['id']:02d} [{t['assigned_to']:22}] {t['title'][:38]}")
    print(f"{'='*55}\n")

if __name__ == "__main__":
    cmds = {
        "init": lambda: init_team(),
        "status": lambda: status(),
        "approve": lambda: approve_plan(int(sys.argv[2])),
        "complete": lambda: complete_task(int(sys.argv[2])),
        "broadcast": lambda: broadcast(sys.argv[2], sys.argv[3]),
        "msg": lambda: send_message(sys.argv[2], sys.argv[3], sys.argv[4]),
    }
    if len(sys.argv) > 1 and sys.argv[1] in cmds:
        cmds[sys.argv[1]]()
    else:
        print("Uso: python team_manager.py [init|status|approve|complete|broadcast|msg]")
