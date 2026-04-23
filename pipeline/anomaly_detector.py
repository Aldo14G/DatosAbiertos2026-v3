def detect_low_global_score(dataset: dict, threshold: float = 50.0) -> bool:
    """Verifica si el score global de un dataset es menor al umbral."""
    score = dataset.get("score_global")
    if score is None:
        return False
    return float(score) < threshold


def detect_critical_dimension(dataset: dict, threshold: float = 30.0) -> bool:
    """Verifica si alguna dimensión individual del dataset cae por debajo del umbral."""
    scores = dataset.get("scores", {})
    if not scores:
        return False
        
    for dim, val in scores.items():
        if val is not None and float(val) < threshold:
            return True
            
    return False


def detect_category_anomaly(datasets: list[dict], variance_threshold: float = 20.0) -> list[dict]:
    """Detecta datasets que tienen una diferencia mayor al threshold respecto al dataset con mayor score en su categoría."""
    categories_max = {}
    
    # 1. Encontrar el score máximo por categoría
    for ds in datasets:
        cat = ds.get("categoria", "Sin Categoria")
        score = ds.get("score_global")
        
        if score is None:
            continue
            
        score = float(score)
        if cat not in categories_max or score > categories_max[cat]:
            categories_max[cat] = score
            
    # 2. Detectar anomalías
    anomalies = []
    for ds in datasets:
        cat = ds.get("categoria", "Sin Categoria")
        score = ds.get("score_global")
        
        if score is None:
            continue
            
        score = float(score)
        max_score = categories_max.get(cat, 0)
        
        if (max_score - score) > variance_threshold:
            anomalies.append(ds)
            
    return anomalies
