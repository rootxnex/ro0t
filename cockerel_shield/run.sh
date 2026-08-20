#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
exec python3 -m streamlit run frontend/app.py \
  --server.address "${HOST:-0.0.0.0}" \
  --server.port "${PORT:-8501}"
