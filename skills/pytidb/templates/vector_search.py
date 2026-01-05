#!/usr/bin/env python3
import json
import os
import sys
from typing import Any, Dict, List

import dotenv

from pytidb import TiDBClient
from pytidb.datatype import JSON as TIDB_JSON
from pytidb.embeddings import EmbeddingFunction
from pytidb.schema import TableModel, Field

dotenv.load_dotenv()


def connect_to_tidb() -> TiDBClient:
    return TiDBClient.connect(
        host=os.getenv("TIDB_HOST", "localhost"),
        port=int(os.getenv("TIDB_PORT", "4000")),
        username=os.getenv("TIDB_USERNAME", "root"),
        password=os.getenv("TIDB_PASSWORD", ""),
        database=os.getenv("TIDB_DATABASE", "vector_search_example"),
        ensure_db=True,
    )


def build_embedder() -> EmbeddingFunction:
    # Demo-friendly multilingual embedding model hosted by TiDB Cloud (no extra API key needed here).
    return EmbeddingFunction(model_name="tidbcloud_free/cohere/embed-multilingual-v3")


def ensure_table(db: TiDBClient, embedder: EmbeddingFunction):
    class Chunk(TableModel):
        __tablename__ = "chunks"
        __table_args__ = {"extend_existing": True}

        id: int = Field(primary_key=True)
        text: str = Field()
        text_vec: list[float] = embedder.VectorField(source_field="text")
        meta: dict = Field(sa_type=TIDB_JSON, default_factory=dict)

    table = db.open_table(Chunk)
    if table is None:
        table = db.create_table(schema=Chunk, if_exists="skip")
    return table


def load_sample_data(table):
    sample_chunks = [
        {"text": "TiDB is a distributed SQL database with HTAP capabilities.", "meta": {"language": "english"}},
        {"text": "TiDB是一个开源的NewSQL数据库，支持混合事务和分析处理（HTAP）工作负载。", "meta": {"language": "chinese"}},
        {"text": "TiDBはオープンソースの分散型HTAPデータベースで、トランザクション処理と分析処理の両方をサポートしています。", "meta": {"language": "japanese"}},
        {"text": "Ollama enables local deployment of large language models.", "meta": {"language": "english"}},
        {"text": "Kubernetes orchestrates containerized applications across clusters.", "meta": {"language": "english"}},
        {"text": "Cybersecurity protects systems from digital attacks.", "meta": {"language": "english"}},
    ]
    Chunk = table.table_model
    table.bulk_insert([Chunk(**chunk) for chunk in sample_chunks])


def main() -> int:
    db = connect_to_tidb()
    embedder = build_embedder()
    table = ensure_table(db, embedder)

    if os.getenv("RESET_SAMPLE_DATA") == "1":
        table.truncate()

    if table.rows() == 0:
        print("Loading sample data...")
        load_sample_data(table)

    query = os.getenv("QUERY") or (sys.argv[1] if len(sys.argv) > 1 else None)
    if not query:
        print('Usage: python example.py "your query"', file=sys.stderr)
        print('Or set env var QUERY="your query"', file=sys.stderr)
        return 2

    language = os.getenv("LANGUAGE", "all").lower()
    limit = int(os.getenv("LIMIT", "10"))
    distance_threshold = float(os.getenv("DISTANCE_THRESHOLD", "0.7"))

    q = table.search(query).distance_threshold(distance_threshold)
    if language != "all":
        q = q.filter({"meta.language": language})

    results: List[Dict[str, Any]] = q.limit(limit).to_list()
    for r in results:
        r.pop("text_vec", None)

    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
