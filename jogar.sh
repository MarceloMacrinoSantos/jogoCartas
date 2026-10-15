#!/bin/sh
# Mac/Linux: cria o ambiente na primeira vez e abre o jogo
cd "$(dirname "$0")"
if ! .venv/bin/python -c "import pygame" 2>/dev/null; then
    rm -rf .venv
    python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt || exit 1
fi
.venv/bin/python visual.py
