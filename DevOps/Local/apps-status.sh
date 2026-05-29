#!/usr/bin/env bash
#
# Status of the natively-run EPAA apps (apps-up.sh): recorded PID alive + port
# listening, per Spring service and portal.
#
# Usage: apps-status.sh [all|middleware|portals]   (default: all)
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="$ROOT/.env"
RUN_DIR="$ROOT/DevOps/Local/.run"
TARGET="${1:-all}"

set -a; [ -f "$ENV_FILE" ] && . "$ENV_FILE"; set +a

log() { printf '\033[0;36m[epaa-apps]\033[0m %s\n' "$*"; }

rows() {  # name port
  local name="$1" port="$2" pidf="$RUN_DIR/$name.pid" pid="-" up="stopped" listening="no"
  if [ -f "$pidf" ]; then
    pid="$(cat "$pidf")"
    kill -0 "$pid" 2>/dev/null && up="running" || { up="dead"; pid="-"; }
  fi
  if command -v lsof >/dev/null 2>&1 && lsof -ti tcp:"$port" >/dev/null 2>&1; then listening="yes"; fi
  printf "  %-22s pid=%-8s %-8s port %-5s listening=%s\n" "$name" "$pid" "$up" "$port" "$listening"
}

echo
log "EPAA native apps ($TARGET)"
case "$TARGET" in all|middleware)
  rows employee-service     "${EMPLOYEE_SERVICE_PORT:-8081}"
  rows project-service      "${PROJECT_SERVICE_PORT:-8082}"
  rows allocation-service   "${ALLOCATION_SERVICE_PORT:-8083}"
  rows notification-service "${NOTIFICATION_SERVICE_PORT:-8084}"
  rows reporting-service    "${REPORTING_SERVICE_PORT:-8085}"
  rows api-gateway          "${API_GATEWAY_PORT:-8080}"
;; esac
case "$TARGET" in all|portals)
  rows admin-portal    "${ADMIN_PORTAL_PORT:-4200}"
  rows projects-portal "${PROJECTS_PORTAL_PORT:-4201}"
;; esac
echo
log "logs: $RUN_DIR/<name>.log"
