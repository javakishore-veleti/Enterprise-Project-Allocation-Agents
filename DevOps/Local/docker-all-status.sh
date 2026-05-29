#!/usr/bin/env bash
#
# Show the status of the EPAA local stack: running containers, health, and the
# handy local URLs.
#
# Usage:
#   docker-all-status.sh [target]
# Targets: all (default) | docker (backing layer) | apps (middleware + portals)
#
set -uo pipefail

NETWORK="epaa-net"
TARGET="${1:-all}"

# Container-name filters per layer (matches start_docker / start_apps in docker-all-up.sh).
DOCKER_NAMES=(epaa-postgres epaa-prometheus epaa-jaeger epaa-grafana epaa-elasticsearch
              epaa-kibana epaa-airflow epaa-datalake-api epaa-agents)
APPS_NAMES=(epaa-employee-service epaa-project-service epaa-allocation-service
            epaa-notification-service epaa-reporting-service epaa-api-gateway
            epaa-admin-portal epaa-projects-portal)

log() { printf '\033[0;36m[epaa]\033[0m %s\n' "$*"; }

command -v docker >/dev/null 2>&1 || { echo "docker not found" >&2; exit 1; }

FILTERS=()
case "$TARGET" in
  all)    FILTERS=(--filter "name=epaa-") ;;
  docker) for n in "${DOCKER_NAMES[@]}"; do FILTERS+=(--filter "name=$n"); done ;;
  apps)   for n in "${APPS_NAMES[@]}";   do FILTERS+=(--filter "name=$n"); done ;;
  *) echo "unknown target '$TARGET' (try: all|docker|apps)" >&2; exit 1 ;;
esac

echo
log "EPAA containers (${TARGET} layer)"
docker ps -a \
  "${FILTERS[@]}" \
  --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" \
  || true

echo
if docker network inspect "$NETWORK" >/dev/null 2>&1; then
  log "network '$NETWORK' present"
else
  log "network '$NETWORK' not created yet (run docker-all-up.sh)"
fi

echo
log "Local URLs (once the matching layer is up)"
cat <<'EOF'
  Postgres        localhost:5432   (db/user: epaa)
  Prometheus      http://localhost:9090
  Grafana         http://localhost:3000   (admin/admin)
  Jaeger UI       http://localhost:16686
  Agents API      http://localhost:8001   (M3)
  API Gateway     http://localhost:8080   (M4)
  Admin Portal    http://localhost:4200   (M5)
  Projects Portal http://localhost:4201   (M5)
EOF
echo
