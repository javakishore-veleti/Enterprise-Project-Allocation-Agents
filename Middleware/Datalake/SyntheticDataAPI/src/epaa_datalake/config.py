"""Runtime configuration, sourced from environment (.env at repo root)."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    # Database (Datalake/agents always use Postgres + pgvector)
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "epaa"
    postgres_user: str = "epaa"
    postgres_password: str = "epaa_local"

    # Embeddings
    embedding_provider: str = "hash"  # bedrock | hf | hash (offline deterministic fallback)
    embedding_dim: int = 1024  # Titan v2 = 1024 (must match the pgvector column dimension)
    bedrock_embedding_model_id: str = "amazon.titan-embed-text-v2:0"
    hf_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    aws_region: str = "us-east-1"

    # LLM (optional, for --use-llm text generation)
    bedrock_model_id: str = "us.anthropic.claude-opus-4-7-v1:0"

    # Airflow REST (for the API to trigger the DAG)
    airflow_base_url: str = "http://localhost:8088"
    airflow_user: str = "admin"
    airflow_password: str = "admin"
    synthetic_dag_id: str = "synthetic_data_gen"

    @property
    def sqlalchemy_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
