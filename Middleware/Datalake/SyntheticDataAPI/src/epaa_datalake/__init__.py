"""EPAA Datalake — synthetic data generation for the MCP-AI platform.

Generates the relational data (employees, skills, projects, availability), the
unstructured text (project briefs, employee profile bios), and the pgvector
embeddings that the agents reason over. Exposed as a FastAPI service that
triggers an Airflow DAG; the same generation logic is importable by the DAG.
"""

__version__ = "0.1.0"
