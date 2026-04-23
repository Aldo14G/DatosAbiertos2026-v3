import pytest
from anomaly_detector import detect_low_global_score, detect_critical_dimension, detect_category_anomaly

# 1. Test: score_global < 50 detecta dataset problemático
def test_global_score_anomaly():
    dataset_good = {"slug": "good", "score_global": 85.0}
    dataset_bad = {"slug": "bad", "score_global": 45.0}
    
    assert detect_low_global_score(dataset_good) == False
    assert detect_low_global_score(dataset_bad) == True

# 2. Test: cualquier dimensión < 30 detecta anomalía
def test_critical_dimension_anomaly():
    scores_good = {"completeness": 90, "accuracy": 80, "consistency": 70, "uniqueness": 60}
    dataset_good = {"slug": "good", "scores": scores_good}
    
    scores_bad = {"completeness": 90, "accuracy": 29, "consistency": 70, "uniqueness": 60}
    dataset_bad = {"slug": "bad", "scores": scores_bad}
    
    assert detect_critical_dimension(dataset_good) == False
    assert detect_critical_dimension(dataset_bad) == True

# 3. Test: diff > 20% entre scores de misma categoría
def test_category_anomaly():
    datasets = [
        {"slug": "ds1", "categoria": "Finanzas", "score_global": 80.0},
        {"slug": "ds2", "categoria": "Finanzas", "score_global": 75.0},
        {"slug": "ds3", "categoria": "Finanzas", "score_global": 50.0}, # Anomalía: 80 - 50 = 30 > 20
        {"slug": "ds4", "categoria": "Salud", "score_global": 90.0},
        {"slug": "ds5", "categoria": "Salud", "score_global": 85.0}
    ]
    
    anomalies = detect_category_anomaly(datasets)
    assert len(anomalies) == 1
    assert anomalies[0]["slug"] == "ds3"
