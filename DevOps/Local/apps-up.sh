#!/usr/bin/env bash
#
# Run the EPAA apps NATIVELY (no Docker): the 6 Spring Boot services via
# `mvn spring-boot:run` and the 2 Angular portals via `ng serve`. The backing
# services (Postgres, agents, Datalake, Airflow, observability) stay in Docker —
# start them first with `npm run local:docker:start-all`.
#
# Needs host JDK 21 + Maven + Node. PIDs and logs live under DevOps/Local/.run/.
# Ports + DB come from the root .env (DB_PROFILE=postgres points Spring at the
# Dockerized Postgres on localhost:5432; secrets:gen materialises that).
#
# Usage: apps-up.sh [all|middleware|portals]   (default: all)
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="$ROOT/.env"
RUN_DIR="$ROOT/DevOps/Local/.run"
TARGET="${1:-all}"
mkdir -p "$RUN_DIR"

# Export everything in .env so service ${PORT}/${DB} placeholders resolve.
set -a; [ -f "$ENV_FILE" ] && . "$ENV_FILE"; set +a

log()  { printf '\033[0;36m[epaa-apps]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[epaa-apps]\033[0m %s\n' "$*"; }
die()  { printf '\033[0;31m[epaa-apps]\033[0m %s\n' "$*" >&2; exit 1; }

command -v mvn  >/dev/null 2>&1 || die "mvn not found — native apps need Maven + JDK 21."
command -v java >/dev/null 2>&1 || die "java not found — native apps need JDK 21."

_running() {  # pidfile -> 0 if a live PID is recorded
  local pidf="$1"
  [ -f "$pidf" ] && kill -0 "$(cat "$pidf")" 2>/dev/null
}

# start_spring <name> <service-dir> <api-module> <port>
start_spring() {
  local name="$1" dir="$2" api="$3" port="$4"
  local pidf="$RUN_DIR/$name.pid" logf="$RUN_DIR/$name.log"
  if _running "$pidf"; then warn "$name already running (pid $(cat "$pidf"))"; return 0; fi
  log "building $name (mvn install — first run is slow, logs: .run/$name.log)"
  if ! mvn -q -DskipTests -f "$ROOT/Middleware/$dir/pom.xml" install >"$logf" 2>&1; then
    warn "$name build failed — see $logf"; return 1
  fi
  log "starting $name on :$port"
  # fork=false keeps the app in this mvn JVM so the recorded PID is killable.
  ( cd "$ROOT/Middleware/$dir" \
      && nohup mvn -q -pl "$api" -Dspring-boot.run.fork=false spring-boot:run \
           >>"$logf" 2>&1 &
    echo $! >"$pidf" )
}

# start_portal <name> <portal-dir> <port>
start_portal() {
  local name="$1" dir="$2" port="$3"
  local pidf="$RUN_DIR/$name.pid" logf="$RUN_DIR/$name.log"
  if _running "$pidf"; then warn "$name already running (pid $(cat "$pidf"))"; return 0; fi
  [ -x "$ROOT/Portals/$dir/node_modules/.bin/ng" ] || { warn "$name: node_modules missing — run 'npm --prefix Portals/$dir install'"; return 1; }
  log "starting $name on :$port (ng serve)"
  ( cd "$ROOT/Portals/$dir" \
      && nohup ./node_modules/.bin/ng serve --port "$port" --host 0.0.0.0 \
           >"$logf" 2>&1 &
    echo $! >"$pidf" )
}

start_middleware() {
  start_spring employee-service     employee-service     employee-api     "${EMPLOYEE_SERVICE_PORT:-8081}"
  start_spring project-service      project-service      project-api      "${PROJECT_SERVICE_PORT:-8082}"
  start_spring allocation-service   allocation-service   allocation-api   "${ALLOCATION_SERVICE_PORT:-8083}"
  start_spring notification-service notification-service notification-api "${NOTIFICATION_SERVICE_PORT:-8084}"
  start_spring reporting-service    reporting-service    reporting-api    "${REPORTING_SERVICE_PORT:-8085}"
  start_spring api-gateway          api-gateway          gateway-api      "${API_GATEWAY_PORT:-8080}"
}

start_portals() {
  start_portal admin-portal    admin-portal    "${ADMIN_PORTAL_PORT:-4200}"
  start_portal projects-portal projects-portal "${PROJECTS_PORTAL_PORT:-4201}"
}

case "$TARGET" in
  all)        start_middleware; start_portals ;;
  middleware) start_middleware ;;
  portals)    start_portals ;;
  *) die "unknown target '$TARGET' (try: all|middleware|portals)" ;;
esac

log "launched (backgrounded). Watch logs: tail -f $RUN_DIR/<name>.log"
log "Spring services need ~20-40s to come up; check: npm run local:apps:status-all"
