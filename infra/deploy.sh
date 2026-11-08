#!/usr/bin/env bash
# Rodar NA EC2: bash infra/deploy.sh   (atualiza o código e recompila o que mudou)
set -euo pipefail
cd "$(dirname "$0")/.."
git pull --ff-only origin main
cd infra
docker compose --env-file ../.env up --build -d --remove-orphans
docker image prune -f
docker compose --env-file ../.env ps
