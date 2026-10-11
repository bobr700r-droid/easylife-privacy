#!/bin/zsh
# Vygeneruje web (zásady + dist/cz, dist/eu) a nasadí ho na Fly. GitHub Pages (docs/) se aktualizují gitem.
set -euo pipefail
cd "${0:A:h}"
python3 build.py
fly deploy --ha=false
