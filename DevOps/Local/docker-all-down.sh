#!/usr/bin/env bash
#
# Tear down the EPAA local stack (reverse order of docker-all-up.sh).
# Volumes are preserved unless you pass --volumes.
#
# Usage:
#   docker-all-down.sh [target] [--volumes]
# Targets: all (default) | infra | postgres | observability | vectordb | agents | middleware | portals
#
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
NETWORK="epaa-net"
ENV_FILE="$ROOT/.env"

TARGET="all"
DOWN_ARGS=()
for arg in "$@"; do
  case "$arg" in
    --volumes|-v) DOWN_ARGS+=("--volumes") ;;
    *)            TARGET="$arg" ;;
  esac
done

POSTGRES_COMPOSE="DevOps/Local/Postgres/docker-compose.yaml"
PROMETHEUS_COMPOSE="DevOps/Local/Observability/Prometheus/docker-compose.yaml"
GRAFANA_COMPOSE="DevOps/Local/Observability/Grafana/docker-compose.yaml"
JAEGER_COMPOSE="DevOps/Local/Observability/Jaeger/docker-compose.yaml"
KIBANA_COMPOSE="DevOps/Local/Observability/Kibana/docker-compose.yaml"
AIRFLOW_COMPOSE="DevOps/Local/Airflow/docker-compose.yaml"
DATALAKE_COMPOSE="DevOps/Local/Datalake/docker-compose.yaml"
QDRANT_COMPOSE="DevOps/Local/VectorDBs/Qdrant/docker-compose.yaml"
AGENTS_COMPOSE="DevOps/Local/Agents/docker-compose.yaml"
MIDDLEWARE_COMPOSE="DevOps/Local/Middleware/docker-compose.yaml"
PORTALS_COMPOSE="DevOps/Local/Portals/docker-compose.yaml"

log()  { printf '\033[0;36m[epaa]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[epaa]\033[0m %s\n' "$*"; }

command -v docker >/dev/null 2>&1 || { echo "docker not found" >&2; exit 1; }

down() {
  local file="$1" name="$2"
  [[ -f "$ROOT/$file" ]] || return 0
  log "stopping $name"
  # shellcheck disable=SC2068
  docker compose --env-file "$ENV_FILE" -f "$ROOT/$file" down ${DOWN_ARGS[@]:-}
}

stop_observability() {
  down "$KIBANA_COMPOSE"     "elasticsearch+kibana"
  down "$GRAFANA_COMPOSE"    "grafana"
  down "$JAEGER_COMPOSE"     "jaeger"
  down "$PROMETHEUS_COMPOSE" "prometheus"
}

stop_infra() {
  stop_observability
  down "$POSTGRES_COMPOSE" "postgres+pgvector"
}

case "$TARGET" in
  all)
    down "$PORTALS_COMPOSE"    "portals"
    down "$MIDDLEWARE_COMPOSE" "middleware"
    down "$AGENTS_COMPOSE"     "agents"
    down "$DATALAKE_COMPOSE"   "datalake-api"
    down "$AIRFLOW_COMPOSE"    "airflow"
    stop_infra
    ;;
  infra)          stop_infra ;;
  postgres)       down "$POSTGRES_COMPOSE" "postgres+pgvector" ;;
  observability)  stop_observability ;;
  airflow)        down "$AIRFLOW_COMPOSE"    "airflow" ;;
  datalake)       down "$DATALAKE_COMPOSE"   "datalake-api" ;;
  vectordb)       down "$QDRANT_COMPOSE"     "qdrant" ;;
  agents)         down "$AGENTS_COMPOSE"     "agents" ;;
  middleware)     down "$MIDDLEWARE_COMPOSE" "middleware" ;;
  portals)        down "$PORTALS_COMPOSE"    "portals" ;;
  *) echo "unknown target '$TARGET'" >&2; exit 1 ;;
esac

# Remove the shared network when nothing is attached (best-effort, only on full down).
if [[ "$TARGET" == "all" ]]; then
  if docker network inspect "$NETWORK" >/dev/null 2>&1; then
    docker network rm "$NETWORK" >/dev/null 2>&1 && log "removed network $NETWORK" || warn "network $NETWORK still in use — left in place"
  fi
fi

log "down complete."
