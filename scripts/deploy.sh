#!/bin/bash
# JEDINÝ způsob nasazení webu EasyForLife: jen kód z origin/main (HEAD == origin/main, čistá kopie), build, fly deploy, ověření.
# Pojistka: ~/EasyLife aplikace/tools/deploy-guard.sh (Zásady provozu 15. 10., bod 3). Spouští uživatel.
# Build přegeneruje docs/ (GitHub Pages) – po nasazení případně commit + push.
set -euo pipefail
GUARD="${DEPLOY_GUARD:-$HOME/EasyLife aplikace/tools/deploy-guard.sh}"
[ -x "$GUARD" ] || { echo "Chybí $GUARD – v ~/EasyLife aplikace spusť git pull."; exit 1; }
cd "$(dirname "$0")/.."
exec "$GUARD" --pre "python3 build.py" --health https://easyforlife-redirect.fly.dev/healthz -- --ha=false
