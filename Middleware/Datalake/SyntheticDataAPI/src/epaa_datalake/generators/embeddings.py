"""Embedding providers: Bedrock Titan, HuggingFace MiniLM, or an offline hash fallback.

The hash fallback is deterministic and dependency-free so the whole pipeline runs
with no AWS and no heavy models — it is NOT semantically meaningful, only a stand-in
for local/offline runs. Use bedrock or hf for real semantic matching.
"""
from __future__ import annotations

import hashlib
import logging
import math

from ..config import get_settings

log = logging.getLogger(__name__)


def _hash_embed(text: str, dim: int) -> list[float]:
    # Expand a sha256 stream to `dim` floats in [-1, 1], then L2-normalise.
    raw = bytearray()
    counter = 0
    while len(raw) < dim * 2:
        raw += hashlib.sha256(f"{text}:{counter}".encode()).digest()
        counter += 1
    vals = [(raw[i] / 127.5) - 1.0 for i in range(dim)]
    norm = math.sqrt(sum(v * v for v in vals)) or 1.0
    return [v / norm for v in vals]


def _bedrock_embed(texts: list[str], dim: int) -> list[list[float]]:
    import json

    import boto3

    s = get_settings()
    client = boto3.client("bedrock-runtime", region_name=s.aws_region)
    out: list[list[float]] = []
    for t in texts:
        body = json.dumps({"inputText": t, "dimensions": dim, "normalize": True})
        resp = client.invoke_model(modelId=s.bedrock_embedding_model_id, body=body)
        out.append(json.loads(resp["body"].read())["embedding"])
    return out


def _hf_embed(texts: list[str], dim: int) -> list[list[float]]:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(get_settings().hf_embedding_model)
    return [v.tolist() for v in model.encode(texts, normalize_embeddings=True)]


def embed_texts(texts: list[str]) -> list[list[float]]:
    s = get_settings()
    dim = s.embedding_dim
    provider = s.embedding_provider.lower()
    if not texts:
        return []
    try:
        if provider == "bedrock":
            return _bedrock_embed(texts, dim)
        if provider == "hf":
            return _hf_embed(texts, dim)
    except Exception as exc:  # noqa: BLE001
        log.warning("Embedding provider '%s' failed (%s); falling back to hash.", provider, exc)
    return [_hash_embed(t, dim) for t in texts]
