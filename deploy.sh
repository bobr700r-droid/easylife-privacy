#!/bin/zsh
# Zástupce – jediný způsob nasazení je scripts/deploy.sh (jen z origin/main).
exec "${0:A:h}/scripts/deploy.sh" "$@"
