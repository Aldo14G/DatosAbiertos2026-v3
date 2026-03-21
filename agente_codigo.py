import json
import os
import time
import datetime
import requests
import io
import warnings
import numpy as np

# Silenciar las advertencias de pandas sobre tipos mixtos para no ensuciar el log
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd

import team_manager

SHARED = team_manager.SHARED
DELAY = 1.6

def log_msg(msg):
    print(f"[Agente Codigo] {msg}")

def read_csv_with_encodings(content):
    encodings = ['utf-8', 'latin-1', 'cp1252']
    separators = [',', ';', '\t']
    
    for sep in separators:
        for enc in encodings:
            try:
                # Usar low_memory=False para mitigar los warnings de tipos mixtos en memoria grande
                df = pd.read_csv(io.StringIO(content.decode(enc)), sep=sep, low_memory=False)
                if not df.empty and len(df.columns) > 1:
                    return df
                elif len(df.columns) == 1 and sep == separators[-1]:
                    return df # Devuelve de todas formas si solo tiene 1 col
            except Exception:
                continue
    return None

def calc_completeness(df):
    total_cells = df.size
    if total_cells == 0: return 0.0
    null_cells = df.isna().sum().sum()
    return round((1.0 - (null_cells / total_cells)) * 100.0, 2)

def calc_accuracy(df):
    score = 100.0
    columns = len(df.columns)
    if columns == 0: return 0.0
    
    penalty_per_col = 15.0 / columns # Penalty of 15 max per column 
    for col in df.columns:
        dtype = pd.api.types.infer_dtype(df[col], skipna=True)
        if dtype == 'mixed' or dtype == 'mixed-integer': # mixed
            score -= penalty_per_col
            
    return max(0.0, round(score, 2))

def calc_consistency(df):
    score = 100.0
    num_cols = df.select_dtypes(include=[np.number]).columns
    str_cols = df.select_dtypes(include=['object']).columns

    outlier_penalty = 0.0
    total_num_cells = 0
    total_outliers = 0
    
    for col in num_cols:
        series = df[col].dropna()
        if not series.empty:
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            outliers = series[(series < (q1 - 1.5 * iqr)) | (series > (q3 + 1.5 * iqr))]
            total_outliers += len(outliers)
            total_num_cells += len(series)
            
    if total_num_cells > 0:
        outlier_percent = total_outliers / total_num_cells
        outlier_penalty = min(20.0, outlier_percent * 100) # Max 20 puntos de penalizacion
        
    inconsistencias_capitalizacion = 0
    total_str_cols = len(str_cols)
    for col in str_cols:
        series = df[col].dropna().astype(str)
        if not series.empty:
            uppers = series.str.isupper().sum()
            lowers = series.str.islower().sum()
            titles = series.str.istitle().sum()
            total = len(series)
            max_pato = max(uppers, lowers, titles)
            if max_pato < total * 0.8: # Si no hay un estilo dominante al >80%
                inconsistencias_capitalizacion += 1

    cap_penalty = 0.0
    if total_str_cols > 0:
        cap_penalty = (inconsistencias_capitalizacion / total_str_cols) * 15.0 # Max 15 ptos de penalty
        
    score = score - outlier_penalty - cap_penalty
    return max(0.0, round(score, 2))

def calc_uniqueness(df):
    if len(df) == 0: return 0.0
    dups = df.duplicated().sum()
    pct_unique = 1.0 - (dups / len(df))
    return round(pct_unique * 100.0, 2)

def run():
    log_msg("Iniciando Agente Codigo: Procesamiento Analitico")
    
    # Validar dependencias (datasets_index.json)
    index_path = f"{SHARED}/datasets_index.json"
    if not os.path.exists(index_path):
        log_msg("Error: datasets_index.json no existe. Corre al investigador primero.")
        return
        
    with open(index_path, "r", encoding='utf-8') as f:
        datasets = json.load(f)
        
    procesados_info = []
    
    fallidos = 0
    exitosos = 0
    
    # Procesar todo
    for ds in datasets:
        # Filtrar el mejor recurso CSV del data set
        csvs = [r for r in ds.get("resources", []) if r.get("format", "").upper() in ("CSV", "TXT", "TSV") and r.get("status_code") == 200]
        
        if not csvs:
            # Dataset no tiene CSV publicos o estan rotos
            log_msg(f"Omitiendo {ds['name']}: No hay CSVs validos accesibles.")
            continue
            
        csv = csvs[0] # Tomar el primero principal
        url = csv.get("url")
        log_msg(f"Procesando {ds['name']} -> URL: {url} ...")
        
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            df = read_csv_with_encodings(resp.content)
            
            if df is not None and not df.empty:
                comp_score = calc_completeness(df)
                acc_score = calc_accuracy(df)
                cons_score = calc_consistency(df)
                uniq_score = calc_uniqueness(df)
                global_score = round(np.mean([comp_score, acc_score, cons_score, uniq_score]), 2)
                
                procesados_info.append({
                  "slug": ds.get("name"),
                  "categoria": ds.get("category"),
                  "organizacion": ds.get("organization"),
                  "filas": len(df),
                  "columnas": len(df.columns),
                  "scores": {
                    "completeness": comp_score,
                    "accuracy": acc_score,
                    "consistency": cons_score,
                    "uniqueness": uniq_score,
                    "global": global_score
                  }
                })
                exitosos += 1
            else:
                procesados_info.append({
                  "slug": ds.get("name"),
                  "categoria": ds.get("category"),
                  "organizacion": ds.get("organization"),
                  "filas": 0,
                  "columnas": 0,
                  "scores": None
                })
                fallidos += 1
                
        except Exception as e:
            log_msg(f"Fallido archivo: {url} -> Error: {e}")
            procesados_info.append({
                  "slug": ds.get("name"),
                  "categoria": ds.get("category"),
                  "organizacion": ds.get("organization"),
                  "filas": 0,
                  "columnas": 0,
                  "scores": None
            })
            fallidos += 1
        
        time.sleep(DELAY)
        
    # Escribir results schema (T14)
    # Lock output
    lock_file = f"{team_manager.TEAM_DIR}/locks/quality_results.lock"
    with open(lock_file, "w") as f:
        f.write(str(os.getpid()))
        
    final_output = {
      "metadata": {
        "generado": str(datetime.date.today()),
        "datasets_procesados": exitosos + fallidos,
        "version_script": "2.0"
      },
      "datasets": procesados_info
    }
    
    with open(f"{SHARED}/quality_results.json", "w", encoding='utf-8') as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
        
    os.remove(lock_file)
    
    # Marcar completadas: 7 a 15
    for task_id in range(7, 16):
        team_manager.complete_task(task_id)
        
    # Notificar a AldoGbot (T15)
    log_msg(f"Procesamiento listo: {exitosos} completados, {fallidos} fallidos.")
    team_manager.send_message("agente_codigo", "AldoGbot", f"Analisis estadistico completo. datasets procesados: {exitosos+fallidos}. Fallidos: {fallidos}")
    team_manager.broadcast("agente_codigo", "Score global calculado. quality_results.json listo en shared.")
    
if __name__ == "__main__":
    run()
