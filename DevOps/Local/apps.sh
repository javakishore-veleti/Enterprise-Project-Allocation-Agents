#!/usr/bin/env bash
#
# EPAA apps — one native runner (no Docker): start | stop | status.
#
#   apps.sh start  [all|middleware|portals]   (default target: all)
#   apps.sh stop   [all|middleware|portals]
#   apps.sh status [all|middleware|portals]
#
# Each app runs INDEPENDENTLY: the 6 Spring services via `mvn spring-boot:run`,
# the 2 Angular portals via `ng serve` — backgrounded, with a PID + log under
# DevOps/Local/.run/. Needs host JDK 21 + Maven + Node. Ports/DB come from .env
# (DB_PROFILE=postgres points Spring at the Dockerised Postgres on localhost).
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="$ROOT/.env"
RUN_DIR="$ROOT/DevOps/Local/.run"
CMD="${1:-}"; TARGET="${2:-all}"
mkdir -p "$RUN_DIR"
set -a; [ -f "$ENV_FILE" ] && . "$ENV_FILE"; set +a

log()  { printf '\033[0;36m[epaa-apps]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[epaa-apps]\033[0m %s\n' "$*"; }

MW_NAMES="employee-service project-service allocation-service notification-service reporting-service api-gateway"
PT_NAMES="admin-portal projects-portal"

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

alive() { [ -f "$RUN_DIR/$1.pid" ] && kill -0 "$(cat "$RUN_DIR/$1.pid")" 2>/dev/null; }

# start_spring <name> <service-dir> <api-module|''>   ('' = single-module app, e.g. gateway)
start_spring() {
  local name="$1" dir="$2" api="$3" port logf="$RUN_DIR/$1.log"
  port="$(port_of "$name")"
  alive "$name" && { warn "$name already running"; return; }
  log "build + start $name on :$port  (log: .run/$name.log)"
  if ! mvn -q -DskipTests -f "$ROOT/Middleware/$dir/pom.xml" install >"$logf" 2>&1; then
    warn "$name build failed — see .run/$name.log"; return
  fi
  local sel=""; [ -n "$api" ] && sel="-pl $api"   # multi-module: run only the -api module
  # fork=false keeps the app in this mvn JVM, so the recorded PID is killable.
  ( cd "$ROOT/Middleware/$dir" \
      && nohup mvn -q $sel -Dspring-boot.run.fork=false spring-boot:run >>"$logf" 2>&1 &
    echo $! >"$RUN_DIR/$name.pid" )
}

# start_portal <name> <portal-dir>
start_portal() {
  local name="$1" dir="$2" port logf="$RUN_DIR/$1.log"
  port="$(port_of "$name")"
  alive "$name" && { warn "$name already running"; return; }
  [ -x "$ROOT/Portals/$dir/node_modules/.bin/ng" ] || { warn "$name: run 'npm --prefix Portals/$dir install' first"; return; }
  log "start $name on :$port  (log: .run/$name.log)"
  ( cd "$ROOT/Portals/$dir" \
      && nohup ./node_modules/.bin/ng serve --port "$port" --host 0.0.0.0 >"$logf" 2>&1 &
    echo $! >"$RUN_DIR/$name.pid" )
}

stop_one() {
  local name="$1" pidf="$RUN_DIR/$1.pid" pid
  [ -f "$pidf" ] || return 0
  pid="$(cat "$pidf")"
  if kill -0 "$pid" 2>/dev/null; then
    log "stop $name (pid $pid)"
    kill "$pid" 2>/dev/null
    for _ in 1 2 3 4 5; do kill -0 "$pid" 2>/dev/null || break; sleep 1; done
    kill -9 "$pid" 2>/dev/null || true
  fi
  rm -f "$pidf"
}

status_one() {
  local name="$1" pidf="$RUN_DIR/$1.pid" pid="-" state="stopped"
  if [ -f "$pidf" ]; then
    pid="$(cat "$pidf")"
    if kill -0 "$pid" 2>/dev/null; then state="running"; else state="dead"; pid="-"; fi
  fi
  printf "  %-22s %-8s pid=%-8s :%s\n" "$name" "$state" "$pid" "$(port_of "$name")"
}

start_middleware() {
  start_spring employee-service     employee-service     employee-api
  start_spring project-service      project-service      project-api
  start_spring allocation-service   allocation-service   allocation-api
  start_spring notification-service notification-service notification-api
  start_spring reporting-service    reporting-service    reporting-api
  start_spring api-gateway          api-gateway          ""
}
start_portals() { start_portal admin-portal admin-portal; start_portal projects-portal projects-portal; }

names_for() {
  case "$1" in
    all) echo "$MW_NAMES $PT_NAMES" ;; middleware) echo "$MW_NAMES" ;; portals) echo "$PT_NAMES" ;;
  esac
}

usage() { echo "usage: apps.sh <start|stop|status> [all|middleware|portals]" >&2; exit 1; }

case "$CMD" in
  start)
    command -v mvn >/dev/null 2>&1 || { warn "mvn not found — native apps need Maven + JDK 21."; exit 1; }
    case "$TARGET" in
      all)        start_middleware; start_portals ;;
      middleware) start_middleware ;;
      portals)    start_portals ;;
      *) usage ;;
    esac
    log "started ($TARGET). Apps need ~20-40s; check: npm run local:apps:status-all"
    ;;
  stop)
    names="$(names_for "$TARGET")"; [ -z "$names" ] && usage
    for n in $names; do stop_one "$n"; done
    log "stopped ($TARGET)."
    ;;
  status)
    [ -n "$(names_for "$TARGET")" ] || usage
    echo; log "EPAA native apps ($TARGET)"
    case "$TARGET" in all|middleware) for n in $MW_NAMES; do status_one "$n"; done ;; esac
    case "$TARGET" in all|portals)    for n in $PT_NAMES; do status_one "$n"; done ;; esac
    echo; log "logs under DevOps/Local/.run/<name>.log"
    ;;
  *) usage ;;
esac
