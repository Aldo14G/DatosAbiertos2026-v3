import os
import time
import json
import datetime
import requests
import traceback
from collections import defaultdict

import team_manager

API_URL = "https://catalogodatos.nl.gob.mx/api/3/action/package_search"
DELAY = 1.6  # Un poco mas de 1.5s para asegurar

def log_msg(msg):
    print(f"[Investigador] {msg}")

def check_url(url):
    """Realiza un HEAD o GET ligero para verificar si la URL responde 200 sin descargar."""
    try:
        # Algunos servidores no soportan HEAD, pero intentamos primero
        response = requests.head(url, allow_redirects=True, timeout=10)
        if response.status_code == 200:
            return 200, False
        
        # Fallback a GET con stream=True
        response = requests.get(url, stream=True, allow_redirects=True, timeout=10)
        status = response.status_code
        response.close()
        return status, status != 200
    except requests.RequestException as e:
        return 0, True

def run():
    log_msg("Iniciando auditoria del portal Datos Abiertos NL...")
    
    # Asegurarnos de tener el lock de T4..5 si es necesario
    lock_path = f"{team_manager.TEAM_DIR}/locks/task_5.lock"
    with open(lock_path, 'w') as f:
        f.write(str(os.getpid()))

    # T1: Descubrir todos los datasets
    log_msg("Consultando API CKAN para listar todos los datasets (T1)...")
    try:
        resp = requests.get(f"{API_URL}?rows=1000")
        resp.raise_for_status()
        data = resp.json()
        packages = data.get('result', {}).get('results', [])
        log_msg(f"Se encontraron {len(packages)} datasets.")
    except Exception as e:
        log_msg(f"Error al conectar con CKAN: {e}")
        return

    time.sleep(DELAY)

    # T2 & T3: Registrar metadatos y detectar nuevos
    datasets = []
    categorias = set()
    formatos = defaultdict(int)
    
    nuevos_datasets_2025_2026 = 0
    
    log_msg("Procesando metadatos y urls de recursos (T2 & T3)...")
    for pkg in packages:
        # Extraccion de categoria (groups o tags)
        cats = [g.get('display_name') or g.get('name', '') for g in pkg.get('groups', [])]
        if not cats and pkg.get('tags'):
            cats = [pkg['tags'][0].get('display_name')]
        categoria = cats[0] if cats else "Sin Categoria"
        categorias.add(categoria)
        
        org = pkg.get('organization', {})
        organizacion = org.get('title') or org.get('name') or "Desconocida"
        
        # Validar creacion vs 2024
        # Si la fecha de creacion es > 2024-12-31, se asume nuevo para nuestro dif
        created_str = pkg.get('metadata_created', '2024-01-01')
        if created_str >= "2025-01-01":
            nuevos_datasets_2025_2026 += 1

        resources = []
        for res in pkg.get('resources', []):
            fmt = str(res.get('format', 'UNKNOWN')).upper().strip()
            if not fmt:
                fmt = 'UNKNOWN'
            formatos[fmt] += 1
            
            resources.append({
                "id": res.get("id"),
                "name": res.get("name"),
                "format": fmt,
                "url": res.get("url"),
                "created": res.get("created"),
                "last_modified": res.get("last_modified") or pkg.get("metadata_modified"),
                "status_code": None,
                "is_broken": None
            })
            
        datasets.append({
            "id": pkg.get("id"),
            "name": pkg.get("name"),
            "title": pkg.get("title"),
            "category": categoria,
            "organization": organizacion,
            "metadata_created": pkg.get("metadata_created"),
            "metadata_modified": pkg.get("metadata_modified"),
            "resources": resources
        })

    # T4: Verificar accesibilidad (HTTP 200) de cada URL de CSV principal
    urls_rotas_count = 0
    total_recursos = sum(len(d['resources']) for d in datasets)
    procesados = 0
    
    log_msg(f"Verificando accesibilidad de {total_recursos} recursos. Esto tomara aprox {total_recursos * DELAY / 60:.1f} minutos (T4)...")
    
    for ds in datasets:
        for res in ds['resources']:
            url = res['url']
            if url:
                status, is_broken = check_url(url)
                res['status_code'] = status
                res['is_broken'] = is_broken
                if is_broken:
                    urls_rotas_count += 1
            else:
                res['status_code'] = 404
                res['is_broken'] = True
                urls_rotas_count += 1
                
            procesados += 1
            if procesados % 10 == 0:
                log_msg(f" Progreso: {procesados}/{total_recursos} recursos revisados, Rotas detectadas: {urls_rotas_count}")
                
            time.sleep(DELAY)
            
    # T5: Escribir portal_snapshot_2026.json y datasets_index.json
    snapshot = {
      "fecha_snapshot": str(datetime.date.today()),
      "total_datasets": len(datasets),
      "datasets_nuevos_vs_2024": nuevos_datasets_2025_2026,
      "urls_rotas": urls_rotas_count,
      "categorias": len(categorias),
      "formatos": dict(formatos)
    }

    log_msg("Escribiendo shared/portal_snapshot_2026.json y shared/datasets_index.json (T5)...")
    
    with open(f"{team_manager.SHARED}/datasets_index.json", "w", encoding='utf-8') as f:
        json.dump(datasets, f, indent=2, ensure_ascii=False)
        
    with open(f"{team_manager.SHARED}/portal_snapshot_2026.json", "w", encoding='utf-8') as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
        
    if os.path.exists(lock_path):
        os.remove(lock_path)

    # Completar todas las tareas (1-6)
    for i in range(1, 7):
        team_manager.complete_task(i)
        
    # T6: Notificar a AldoGbot con resumen
    resumen = f"Auditoria completa. {snapshot['total_datasets']} datasets, {snapshot['urls_rotas']} URLs rotas, {snapshot['categorias']} categorias. Lock liberado."
    team_manager.send_message("agente_investigador", "AldoGbot", resumen)
    team_manager.broadcast("agente_investigador", "Archivos de indice y snapshot generados con exito en /shared.")
    log_msg("Ejecucion como Agente Investigador terminada.")

if __name__ == "__main__":
    run()
