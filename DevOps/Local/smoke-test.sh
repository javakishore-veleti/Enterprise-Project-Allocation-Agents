#!/usr/bin/env bash
#
# End-to-end smoke test of the paper's core flow, containerised:
#   Postgres + Datalake API + Agents service.
# Seeds synthetic data, runs the 6-agent allocation pipeline over HTTP, and
# reads back the managerial report — proving brief → agents → allocation + report.
#
# Offline by default (hash embeddings, heuristic LLM). Set EMBEDDING_PROVIDER=bedrock
# and LLM_PROVIDER=auto (with AWS creds) for the real models.
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
export EMBEDDING_PROVIDER="${EMBEDDING_PROVIDER:-hash}"
export LLM_PROVIDER="${LLM_PROVIDER:-heuristic}"
ENV_FILE="$ROOT/.env"
[[ -f "$ENV_FILE" ]] || cp "$ROOT/.env.example" "$ENV_FILE"

log() { printf '\033[0;36m[smoke]\033[0m %s\n' "$*"; }

docker network create epaa-net >/dev/null 2>&1 || true

log "starting postgres + datalake + agents..."
docker compose --env-file "$ENV_FILE" -f DevOps/Local/Postgres/docker-compose.yaml up -d postgres
docker compose --env-file "$ENV_FILE" -f DevOps/Local/Datalake/docker-compose.yaml up -d --build
docker compose --env-file "$ENV_FILE" -f DevOps/Local/Agents/docker-compose.yaml up -d --build

wait_health() {
  local url="$1" name="$2"
  for _ in $(seq 1 60); do
    curl -sf "$url" >/dev/null 2>&1 && { log "$name up"; return 0; }
    sleep 2
  done
  log "ERROR: $name did not become healthy"; exit 1
}
wait_health http://localhost:8000/health datalake
wait_health http://localhost:8001/health agents

log "seeding synthetic data (sync)..."
curl -s -X POST http://localhost:8000/synthetic/generate \
  -H 'content-type: application/json' \
  -d '{"num_employees":40,"num_projects":10,"seed":11,"use_llm":false,"run_async":false}' >/dev/null

pg_user="${POSTGRES_USER:-epaa}"
pg_db="${POSTGRES_DB:-epaa}"
pid="$(docker exec epaa-postgres psql -U "$pg_user" -d "$pg_db" -t -A -c 'SELECT project_id FROM epaa.project_briefs LIMIT 1;' | tr -d '[:space:]')"
log "running allocation pipeline for project ${pid}"
curl -s -X POST http://localhost:8001/allocations/run \
  -H 'content-type: application/json' -d "{\"project_id\":\"${pid}\"}"
echo
log "managerial report:"
curl -s "http://localhost:8001/reports/${pid}"
echo
log "done. Tear down with: bash DevOps/Local/docker-all-down.sh all"
