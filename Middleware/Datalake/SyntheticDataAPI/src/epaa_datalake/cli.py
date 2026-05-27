"""CLI: `epaa-datalake migrate` and `epaa-datalake generate`.

Also used by the Airflow DAG tasks (importable functions in generators.pipeline).
"""
from __future__ import annotations

import argparse
import json
import logging

from .generators.structured import GenSpec
from .generators.pipeline import run as run_pipeline
from .startup import run_migrations


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(prog="epaa-datalake")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("migrate", help="apply Alembic migrations (upgrade head)")

    g = sub.add_parser("generate", help="generate synthetic data")
    g.add_argument("--employees", type=int, default=60)
    g.add_argument("--projects", type=int, default=20)
    g.add_argument("--seed", type=int, default=42)
    g.add_argument("--use-llm", action="store_true", help="rewrite text via Bedrock Claude")
    g.add_argument("--no-persist", action="store_true", help="generate only; do not write to DB")
    g.add_argument("--migrate-first", action="store_true", help="run migrations before generating")

    args = parser.parse_args(argv)

    if args.cmd == "migrate":
        run_migrations()
        return 0

    if args.cmd == "generate":
        if args.migrate_first:
            run_migrations()
        spec = GenSpec(num_employees=args.employees, num_projects=args.projects,
                       seed=args.seed, use_llm=args.use_llm)
        summary = run_pipeline(spec, persist=not args.no_persist)
        print(json.dumps(summary, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
