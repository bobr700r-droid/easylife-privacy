#!/bin/bash
# Web EasyForLife běží na NASu (kontejner nas-web, Cloudflare tunel) – na Fly nic. Nasazení jen z origin/main přes
# EasyLife nas/deploy.sh web (build.py proběhne tam), pak kontrola https://easyforlife.cz/healthz. Spouští Vedení.
set -euo pipefail
WT="${VEDENI_WT:-$HOME/wt/vedeni-main}"
[ -d "$WT/nas" ] || { echo "Chybí $WT (worktree EasyLife aplikace)."; exit 1; }
cd "$WT" && git fetch -q origin && git checkout -q --detach origin/main
NAS_MODE=prod nas/deploy.sh web
curl -fsS https://easyforlife.cz/healthz && echo
