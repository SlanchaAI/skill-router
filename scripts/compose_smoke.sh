#!/bin/sh
set -eu

PROJECT=${COMPOSE_SMOKE_PROJECT:-ingot-smoke}
TIMEOUT=${COMPOSE_SMOKE_TIMEOUT:-180}

cleanup() {
  if [ "${COMPOSE_SMOKE_KEEP:-0}" != "1" ]; then
    docker compose -p "$PROJECT" --profile langfuse-lan down -v --remove-orphans
  fi
}
trap cleanup EXIT INT TERM

wait_for() {
  name=$1
  url=$2
  insecure=${3:-0}
  elapsed=0
  while [ "$elapsed" -lt "$TIMEOUT" ]; do
    if [ "$insecure" = "1" ]; then
      curl -ksSf "$url" >/dev/null 2>&1 && return 0
    else
      curl -sSf "$url" >/dev/null 2>&1 && return 0
    fi
    sleep 2
    elapsed=$((elapsed + 2))
  done
  echo "error: $name did not become healthy at $url within ${TIMEOUT}s" >&2
  docker compose -p "$PROJECT" --profile langfuse-lan ps >&2
  return 1
}

LANGFUSE_PUBLIC_URL=https://localhost:3443 \
  docker compose -p "$PROJECT" --profile langfuse-lan up -d --build \
  mcp ui langfuse-web langfuse-worker langfuse-proxy

wait_for "Langfuse" "http://localhost:3100/api/public/health"
wait_for "Langfuse TLS proxy" "https://localhost:3443/api/public/health" 1

# A plain GET is not a valid MCP session, so any HTTP response proves the listener is reachable.
curl -sS -o /dev/null http://localhost:8000/mcp || [ "$?" -eq 52 ]
echo "compose smoke passed: MCP, Langfuse, and the TLS proxy are reachable"
