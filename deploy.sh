#!/bin/zsh
# Nasadí web EasyForLife na Fly. Nasazuje jen to, co je v gitu: ve zdrojích (build.py, web.py, site/, server/)
# nesmí být necommitnuté změny – jinak by se zveřejnily i rozpracované zásady jiných appek.
# Postup: commitni své změny → ./deploy.sh (git pull, build, fly deploy) → git push (docs/ pro GitHub Pages).
set -euo pipefail
cd "${0:A:h}"
dirty=$(git status --porcelain -- build.py web.py site server Dockerfile fly.toml)
if [[ -n $dirty ]]; then
  print -u2 "Necommitnuté změny ve zdrojích webu – nejdřív je commitni (nebo počkej na jejich autora):"
  print -u2 "$dirty"
  exit 1
fi
git pull -q --rebase --autostash
python3 build.py
fly deploy --ha=false
