#!/usr/bin/env bash
#
# Show the status of the EPAA local stack: running containers, health, and the
# handy local URLs.
#
set -uo pipefail

NETWORK="epaa-net"

log() { printf '\033[0;36m[epaa]\033[0m %s\n' "$*"; }

command -v docker >/dev/null 2>&1 || { echo "docker not found" >&2; exit 1; }

echo
log "EPAA containers"
docker ps -a \
  --filter "name=epaa-" \
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
