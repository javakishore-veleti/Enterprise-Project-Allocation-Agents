# Build context is the Middleware/ directory (so we can install the shared
# epaa_datalake data layer alongside the agents). See DevOps/Local/Agents/.
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

# Shared data layer first (provides the `epaa-datalake` dependency), then agents.
COPY Datalake/SyntheticDataAPI /app/datalake
COPY Agents /app/agents
RUN pip install /app/datalake && pip install /app/agents

EXPOSE 8001
CMD ["uvicorn", "epaa.api.main:app", "--host", "0.0.0.0", "--port", "8001"]
