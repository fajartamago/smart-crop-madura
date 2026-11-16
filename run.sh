#!/usr/bin/env bash
# Skrip cepat menjalankan TANDUR di Linux / Arch Linux

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

if [ ! -d ".venv" ]; then
    echo "Membuat virtual environment (.venv)..."
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
fi

echo "Menjalankan TANDUR..."
.venv/bin/streamlit run app.py
