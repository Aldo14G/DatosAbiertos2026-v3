#!/usr/bin/env bash
# run_local.sh — DatosAbiertos NL 2026
# Uso: bash run_local.sh
# No requiere venv. Usa el Python del sistema.
set -e

cd "$(dirname "$0")"

echo "[python] $(python --version 2>&1)"

echo "[deps] verificando dependencias..."
python -m pip install -q -r requirements.txt

echo "[check] verificando imports..."
python -c "import streamlit, pandas, plotly, requests, pydantic; print('  core deps OK')"
python -c "import config, data_layer; print('  project modules OK')"

echo ""
echo "[run] http://localhost:8501"
echo "      Ctrl+C para detener."
echo ""

USE_BIGQUERY=false streamlit run dashboard_v3.py \
  --server.port 8501 \
  --server.headless false
