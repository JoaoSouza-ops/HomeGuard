#!/usr/bin/env bash
# Atalhos do HomeGuard (Linux/macOS/Git Bash).  Uso: ./hg.sh up | sim | check | ps | logs [servico] | down | reset
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -f .env ]; then cp .env.example .env; echo "[hg] .env criado a partir do .env.example"; fi
cd infra
DC="docker compose --env-file ../.env --profile lab --profile sim"

urls() {
  echo
  echo "  Dashboard: http://localhost:8080"
  echo "  API docs : http://localhost:8080/api/docs"
  echo
}

case "${1:-ajuda}" in
  up)    $DC up --build -d mosquitto backend web caddy; urls ;;
  sim)   $DC up --build -d; urls; echo "  Simulador de ESPs ligado (MQTT + Telnet em localhost:2323)." ;;
  check) $DC run --rm esp-sim python check.py ;;
  ps)    $DC ps ;;
  logs)  $DC logs -f --tail=100 ${2:+"$2"} ;;
  down)  $DC down ;;
  reset) $DC down -v ;;
  *)
    echo "Uso: ./hg.sh <comando>"
    echo "  up     sobe API + dashboard + broker MQTT"
    echo "  sim    sobe tudo + simulador dos ESPs (para testar sem o hardware)"
    echo "  check  testa API, MQTT e Telnet"
    echo "  ps     mostra o estado dos servicos"
    echo "  logs   acompanha os logs (ex.: ./hg.sh logs backend)"
    echo "  down   para tudo"
    echo "  reset  para tudo e APAGA os dados (banco SQLite)"
    ;;
esac
