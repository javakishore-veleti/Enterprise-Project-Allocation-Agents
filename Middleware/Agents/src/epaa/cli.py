"""CLI: `epaa-agents run --project-id X` (or `--any` to pick one with a brief)."""
from __future__ import annotations

import argparse
import json
import logging

from sqlalchemy import select

from epaa_datalake.db import session_scope
from epaa_datalake.models import ProjectBrief

from . import orchestrator


def _any_project_id() -> str | None:
    with session_scope() as session:
        return session.scalar(select(ProjectBrief.project_id).limit(1))


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(prog="epaa-agents")
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="run the allocation pipeline for a project")
    r.add_argument("--project-id")
    r.add_argument("--any", action="store_true", help="pick any project that has a brief")

    args = parser.parse_args(argv)
    if args.cmd == "run":
        pid = args.project_id or (_any_project_id() if args.any else None)
        if not pid:
            print("no project id (pass --project-id or --any)")
            return 1
        print(json.dumps(orchestrator.run_allocation(pid), indent=2, default=str))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
