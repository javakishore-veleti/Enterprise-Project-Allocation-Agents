#!/usr/bin/env bash
#
# Bring up the EPAA local stack, layer by layer, on a shared docker network.
# Reuses locally-present images (compose pull_policy: missing); only images you
# don't already have are pulled, once.
#
# Usage:
#   docker-all-up.sh [target]
# Targets:
#   all            infra + airflow + agents + middleware + portals  (default)
#   infra          postgres + observability
#   postgres       postgres + pgvector + pgAdmin           (fully local image)
#   observability  prometheus + jaeger + grafana + kibana (+ elasticsearch)
#   airflow        apache airflow (datalake runtime; reuses your local image)
#   vectordb       qdrant (optional, alternative to pgvector)
#   agents         python agents service          (M3 — skipped until it exists)
#   middleware     spring boot services           (M4 — skipped until it exists)
#   portals        angular portals                (M5 — skipped until it exists)
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
NETWORK="epaa-net"
ENV_FILE="$ROOT/.env"
TARGET="${1:-all}"

# compose files relative to repo root
POSTGRES_COMPOSE="DevOps/Local/Postgres/docker-compose.yaml"
PROMETHEUS_COMPOSE="DevOps/Local/Observability/Prometheus/docker-compose.yaml"
GRAFANA_COMPOSE="DevOps/Local/Observability/Grafana/docker-compose.yaml"
JAEGER_COMPOSE="DevOps/Local/Observability/Jaeger/docker-compose.yaml"
KIBANA_COMPOSE="DevOps/Local/Observability/Kibana/docker-compose.yaml"
AIRFLOW_COMPOSE="DevOps/Local/Airflow/docker-compose.yaml"
QDRANT_COMPOSE="DevOps/Local/VectorDBs/Qdrant/docker-compose.yaml"
AGENTS_COMPOSE="DevOps/Local/Agents/docker-compose.yaml"
MIDDLEWARE_COMPOSE="DevOps/Local/Middleware/docker-compose.yaml"
PORTALS_COMPOSE="DevOps/Local/Portals/docker-compose.yaml"

log()  { printf '\033[0;36m[epaa]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[epaa]\033[0m %s\n' "$*"; }
die()  { printf '\033[0;31m[epaa]\033[0m %s\n' "$*" >&2; exit 1; }

command -v docker >/dev/null 2>&1 || die "docker not found on PATH."

ensure_env() {
  if [[ ! -f "$ENV_FILE" ]]; then
    warn ".env not found — creating it from .env.example. Edit it with real AWS/DB values."
    cp "$ROOT/.env.example" "$ENV_FILE"
  fi
}

ensure_network() {
  if ! docker network inspect "$NETWORK" >/dev/null 2>&1; then
    log "creating shared docker network: $NETWORK"
    docker network create "$NETWORK" >/dev/null
  fi
}

up() {
  local file="$1" name="$2"
  if [[ ! -f "$ROOT/$file" ]]; then
    warn "skip $name — not implemented yet ($file)"
    return 0
  fi
  log "starting $name"
  docker compose --env-file "$ENV_FILE" -f "$ROOT/$file" up -d
}

start_observability() {
  up "$PROMETHEUS_COMPOSE" "prometheus"
  up "$JAEGER_COMPOSE"     "jaeger"
  up "$GRAFANA_COMPOSE"    "grafana"
  up "$KIBANA_COMPOSE"     "elasticsearch+kibana"
}

start_infra() {
  up "$POSTGRES_COMPOSE" "postgres+pgvector"
  start_observability
}

ensure_env
ensure_network

case "$TARGET" in
  all)
    start_infra
    up "$AIRFLOW_COMPOSE"    "airflow"
    up "$AGENTS_COMPOSE"     "agents"
    up "$MIDDLEWARE_COMPOSE" "middleware"
    up "$PORTALS_COMPOSE"    "portals"
    ;;
  infra)          start_infra ;;
  postgres)       up "$POSTGRES_COMPOSE" "postgres+pgvector" ;;
  observability)  start_observability ;;
  airflow)        up "$AIRFLOW_COMPOSE"    "airflow" ;;
  vectordb)       up "$QDRANT_COMPOSE"     "qdrant" ;;
  agents)         up "$AGENTS_COMPOSE"     "agents" ;;
  middleware)     up "$MIDDLEWARE_COMPOSE" "middleware" ;;
  portals)        up "$PORTALS_COMPOSE"    "portals" ;;
  *) die "unknown target '$TARGET' (try: all|infra|postgres|observability|airflow|vectordb|agents|middleware|portals)" ;;
esac

log "up complete. Run 'bash DevOps/Local/docker-all-status.sh' to check health."
