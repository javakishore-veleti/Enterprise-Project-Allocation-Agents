#!/usr/bin/env bash
#
# Stop the natively-run EPAA apps started by apps-up.sh (kills the recorded PIDs
# and frees the ports). Also tears down any leftover Dockerised app containers
# (from the older Docker-based apps layer) so a stop always leaves a clean slate.
#
# Usage: apps-down.sh [all|middleware|portals]   (default: all)
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="$ROOT/.env"
RUN_DIR="$ROOT/DevOps/Local/.run"
TARGET="${1:-all}"

set -a; [ -f "$ENV_FILE" ] && . "$ENV_FILE"; set +a

log()  { printf '\033[0;36m[epaa-apps]\033[0m %s\n' "$*"; }

MIDDLEWARE="employee-service project-service allocation-service notification-service reporting-service api-gateway"
PORTALS="admin-portal projects-portal"

# name -> port (to free the port if the PID is already gone)
port_of() {
  case "$1" in
    employee-service)     echo "${EMPLOYEE_SERVICE_PORT:-8081}" ;;
    project-service)      echo "${PROJECT_SERVICE_PORT:-8082}" ;;
    allocation-service)   echo "${ALLOCATION_SERVICE_PORT:-8083}" ;;
    notification-service) echo "${NOTIFICATION_SERVICE_PORT:-8084}" ;;
    reporting-service)    echo "${REPORTING_SERVICE_PORT:-8085}" ;;
    api-gateway)          echo "${API_GATEWAY_PORT:-8080}" ;;
    admin-portal)         echo "${ADMIN_PORTAL_PORT:-4200}" ;;
    projects-portal)      echo "${PROJECTS_PORTAL_PORT:-4201}" ;;
  esac
}

stop_one() {
  local name="$1" pidf="$RUN_DIR/$name.pid" port; port="$(port_of "$name")"
  if [ -f "$pidf" ]; then
    local pid; pid="$(cat "$pidf")"
    if kill -0 "$pid" 2>/dev/null; then
      log "stopping $name (pid $pid)"
      kill "$pid" 2>/dev/null
      for _ in 1 2 3 4 5; do kill -0 "$pid" 2>/dev/null || break; sleep 1; done
      kill -9 "$pid" 2>/dev/null || true
    fi
    rm -f "$pidf"
  fi
  # Fallback: free the port if anything is still bound (orphaned child JVM/ng worker).
  if [ -n "$port" ] && command -v lsof >/dev/null 2>&1; then
    local pids; pids="$(lsof -ti tcp:"$port" 2>/dev/null || true)"
    [ -n "$pids" ] && { log "freeing port $port ($name)"; echo "$pids" | xargs kill -9 2>/dev/null || true; }
  fi
}

names_for() {
  case "$1" in
    all)        echo "$MIDDLEWARE $PORTALS" ;;
    middleware) echo "$MIDDLEWARE" ;;
    portals)    echo "$PORTALS" ;;
    *) echo "" ;;
  esac
}

NAMES="$(names_for "$TARGET")"
[ -z "$NAMES" ] && { echo "unknown target '$TARGET' (try: all|middleware|portals)" >&2; exit 1; }

for n in $NAMES; do stop_one "$n"; done

# Clean up any Docker-run app containers left from the older Docker apps layer.
if command -v docker >/dev/null 2>&1; then
  case "$TARGET" in
    all|middleware) [ -f "$ROOT/DevOps/Local/Middleware/docker-compose.yaml" ] && \
      docker compose --env-file "$ENV_FILE" -f "$ROOT/DevOps/Local/Middleware/docker-compose.yaml" down >/dev/null 2>&1 || true ;;
  esac
  case "$TARGET" in
    all|portals) [ -f "$ROOT/DevOps/Local/Portals/docker-compose.yaml" ] && \
      docker compose --env-file "$ENV_FILE" -f "$ROOT/DevOps/Local/Portals/docker-compose.yaml" down >/dev/null 2>&1 || true ;;
  esac
fi

log "apps stopped ($TARGET)."
