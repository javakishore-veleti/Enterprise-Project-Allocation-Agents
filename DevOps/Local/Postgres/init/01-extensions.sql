-- Runs once on first container init (empty data dir).
-- Extensions required by the EPAA platform.

CREATE EXTENSION IF NOT EXISTS vector;      -- pgvector: embeddings for Skill-Matching Agent
CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- uuid_generate_v4() for primary keys
CREATE EXTENSION IF NOT EXISTS pg_trgm;     -- trigram text search (skill name lookups)
