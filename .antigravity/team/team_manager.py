"""
team_manager.py — Gestor del Equipo AldoGbot
Proyecto: Gobernanza de Datos Abiertos NL 2026

Uso:
    python team_manager.py init          → Inicializa infraestructura
    python team_manager.py status        → Ver estado de tareas
    python team_manager.py complete <id> → Marcar tarea como completada
    python team_manager.py broadcast "<msg>" → Enviar mensaje a todo el equipo
"""
import json
import os
import sys
from datetime import datetime

TEAM_DIR = ".antigravity/team"


def init_team():
    """Inicializa la infraestructura completa del equipo."""
    os.makedirs(f"{TEAM_DIR}/mailbox",                    exist_ok=True)
    os.makedirs(f"{TEAM_DIR}/locks",                      exist_ok=True)
    os.makedirs(f"{TEAM_DIR}/shared/secciones_redactadas",exist_ok=True)

    tasks_path = f"{TEAM_DIR}/tasks.json"
    if not os.path.exists(tasks_path):
        tasks = {
            "proyecto"  : "Gobernanza Datos Abiertos NL 2026",
            "iniciado"  : datetime.now().isoformat(),
            "director"  : "AldoGbot",
            "tasks"     : [
                {
                    "id"      : 1,
                    "titulo"  : "Verificar 9 citas del PDF (Protocolo 3 pasos)",
                    "agente"  : "agente_fuentes",
                    "estado"  : "PENDING",
                    "deps"    : [],
                    "output"  : "shared/fuentes_verificadas.json",
                },
                {
                    "id"      : 2,
                    "titulo"  : "Buscar literatura adicional 2020-2026 (14 queries)",
                    "agente"  : "agente_metodologia",
                    "estado"  : "PENDING",
                    "deps"    : [],
                    "output"  : "shared/literatura_adicional.json",
                },
                {
                    "id"      : 3,
                    "titulo"  : "Mapear variables PDF ↔ data_layer.py + fórmulas LaTeX",
                    "agente"  : "agente_variables",
                    "estado"  : "PENDING",
                    "deps"    : [1],
                    "output"  : "shared/variables_formulas.json",
                },
                {
                    "id"      : 4,
                    "titulo"  : "Redactar secciones 11.1–11.5 + Sección 7 Variables",
                    "agente"  : "agente_redactor",
                    "estado"  : "PENDING",
                    "deps"    : [1, 2, 3],
                    "output"  : "shared/secciones_redactadas/",
                },
                {
                    "id"      : 5,
                    "titulo"  : "Revisar documento: checklist 20 puntos",
                    "agente"  : "agente_revisor",
                    "estado"  : "PENDING",
                    "deps"    : [4],
                    "output"  : "shared/reporte_revision.md",
                },
                {
                    "id"      : 6,
                    "titulo"  : "Consolidar y generar protocolo_investigacion_NL2026_v2.md",
                    "agente"  : "director",
                    "estado"  : "PENDING",
                    "deps"    : [5],
                    "output"  : "protocolo_investigacion_NL2026_v2.md",
                },
            ],
        }
        with open(tasks_path, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)

    # broadcast.msg
    broadcast_path = f"{TEAM_DIR}/broadcast.msg"
    if not os.path.exists(broadcast_path):
        with open(broadcast_path, "w", encoding="utf-8") as f:
            f.write("")

    # Mailboxes individuales
    for agente in ["agente_fuentes","agente_metodologia","agente_variables",
                   "agente_redactor","agente_revisor","director"]:
        mb = f"{TEAM_DIR}/mailbox/{agente}.msg"
        if not os.path.exists(mb):
            with open(mb, "w", encoding="utf-8") as f:
                f.write("")

    print("✓ Infraestructura 'Equipo AldoGbot' lista.")
    print(f"  📁 Directorio base: {TEAM_DIR}/")
    print("  📋 Tareas registradas: 6")
    print("  📬 Mailboxes creados: 6")
    status()


def status():
    """Muestra el estado actual de todas las tareas."""
    tasks_path = f"{TEAM_DIR}/tasks.json"
    if not os.path.exists(tasks_path):
        print("❌ Equipo no inicializado. Ejecuta: python team_manager.py init")
        return

    with open(tasks_path, encoding="utf-8") as f:
        data = json.load(f)

    icons = {
        "PENDING"    : "○",
        "IN_PROGRESS": "◉",
        "COMPLETED"  : "✓",
        "BLOCKED"    : "✗",
        "APPROVED"   : "★",
    }

    print(f"\n📊 EQUIPO ALDOGBOT — {data['proyecto']}")
    print(f"   Iniciado: {data.get('iniciado','—')}")
    print("─" * 70)
    print(f"  {'ID':>3}  {'AGENTE':<24} {'ESTADO':<14} TÍTULO")
    print("─" * 70)
    for t in data["tasks"]:
        icon = icons.get(t["estado"], "?")
        deps = f" [deps:{t['deps']}]" if t.get("deps") else ""
        print(f"  {t['id']:>3}  {t['agente']:<24} {icon} {t['estado']:<12}"
              f" {t['titulo'][:38]}{deps}")
    print()

    completed = sum(1 for t in data["tasks"] if t["estado"] == "COMPLETED")
    total     = len(data["tasks"])
    pct       = completed / total * 100
    bar       = "█" * completed + "░" * (total - completed)
    print(f"  Progreso: [{bar}] {completed}/{total} ({pct:.0f}%)\n")


def complete(task_id: int):
    """Marca una tarea como completada y libera su lock."""
    tasks_path = f"{TEAM_DIR}/tasks.json"
    with open(tasks_path, "r+", encoding="utf-8") as f:
        data = json.load(f)
        found = False
        for t in data["tasks"]:
            if t["id"] == task_id:
                t["estado"]     = "COMPLETED"
                t["completado"] = datetime.now().isoformat()
                found = True
                print(f"✓ Tarea {task_id} ({t['titulo'][:50]}) marcada como COMPLETADA.")
        if found:
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=2, ensure_ascii=False)

    # Liberar lock si existe
    lock_path = f"{TEAM_DIR}/locks/task_{task_id}.lock"
    if os.path.exists(lock_path):
        os.remove(lock_path)
        print(f"  🔓 Lock de tarea {task_id} liberado.")


def broadcast(sender: str, message: str):
    """Envía un mensaje broadcast a todo el equipo."""
    msg = {
        "de"     : sender,
        "tipo"   : "BROADCAST",
        "ts"     : datetime.now().isoformat(),
        "mensaje": message,
    }
    with open(f"{TEAM_DIR}/broadcast.msg", "a", encoding="utf-8") as f:
        f.write(json.dumps(msg, ensure_ascii=False) + "\n")
    print(f"📢 Broadcast enviado por {sender}: {message[:60]}")


def send_message(sender: str, receiver: str, message: str):
    """Envía un mensaje directo al mailbox de un agente."""
    msg = {
        "de"     : sender,
        "ts"     : datetime.now().isoformat(),
        "mensaje": message,
    }
    mb_path = f"{TEAM_DIR}/mailbox/{receiver}.msg"
    os.makedirs(os.path.dirname(mb_path), exist_ok=True)
    with open(mb_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(msg, ensure_ascii=False) + "\n")
    print(f"📨 Mensaje de {sender} → {receiver}: {message[:60]}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "status":
        status()
    elif args[0] == "init":
        init_team()
    elif args[0] == "complete" and len(args) > 1:
        complete(int(args[1]))
    elif args[0] == "broadcast" and len(args) > 2:
        broadcast(args[1], " ".join(args[2:]))
    elif args[0] == "send" and len(args) > 3:
        send_message(args[1], args[2], " ".join(args[3:]))
    else:
        print("Uso:")
        print("  python team_manager.py init")
        print("  python team_manager.py status")
        print("  python team_manager.py complete <id>")
        print('  python team_manager.py broadcast "<sender>" "<mensaje>"')
        print('  python team_manager.py send "<sender>" "<receiver>" "<mensaje>"')
