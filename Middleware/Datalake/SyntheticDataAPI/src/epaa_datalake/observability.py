"""OpenTelemetry tracing setup (shared by the Datalake + Agents FastAPI apps).

No-ops unless OTEL_EXPORTER_OTLP_ENDPOINT is set AND the OTel packages are
installed (the `otel` extra), so base/offline installs are unaffected. Exports
spans (FastAPI requests + SQLAlchemy queries) to the OTLP collector (Jaeger).
"""
from __future__ import annotations

import logging
import os

log = logging.getLogger(__name__)


def setup_tracing(app, service_name: str) -> None:
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        log.info("OTEL endpoint not set — tracing disabled for %s", service_name)
        return
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
        trace.set_tracer_provider(provider)

        FastAPIInstrumentor.instrument_app(app)
        from .db import engine

        SQLAlchemyInstrumentor().instrument(engine=engine())
        log.info("OTEL tracing enabled for %s → %s", service_name, endpoint)
    except Exception as exc:  # noqa: BLE001 — tracing is best-effort
        log.warning("OTEL setup skipped for %s: %s", service_name, exc)
