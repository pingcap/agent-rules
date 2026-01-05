#!/usr/bin/env python3
import os
import sys

import dotenv
import litellm
from litellm import completion

from pytidb import TiDBClient
from pytidb.embeddings import EmbeddingFunction
from pytidb.schema import TableModel, Field

dotenv.load_dotenv()
litellm.drop_params = True

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "ollama/mxbai-embed-large")
LLM_MODEL = os.getenv("LLM_MODEL", "ollama/gemma3:4b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

PROMPT_TEMPLATE = """Context information is below.
---------------------
{context}
---------------------
Given the information and not prior knowledge, answer the query
in a detailed and precise manner.

Query: {question}
Answer:"""


def main() -> int:
    question = os.getenv("QUESTION") or (sys.argv[1] if len(sys.argv) > 1 else None)
    if not question:
        print('Usage: python example.py "your question"', file=sys.stderr)
        print('Or set env var QUESTION="your question"', file=sys.stderr)
        return 2

    db = TiDBClient.connect(
        host=os.getenv("TIDB_HOST", "localhost"),
        port=int(os.getenv("TIDB_PORT", "4000")),
        username=os.getenv("TIDB_USERNAME", "root"),
        password=os.getenv("TIDB_PASSWORD", ""),
        database=os.getenv("TIDB_DATABASE", "rag_example"),
        ensure_db=True,
    )

    text_embed = EmbeddingFunction(EMBEDDING_MODEL)

    class Chunk(TableModel):
        __tablename__ = "chunks"
        __table_args__ = {"extend_existing": True}

        id: int = Field(primary_key=True)
        text: str = Field()
        text_vec: list[float] = text_embed.VectorField(source_field="text")

    table = db.create_table(schema=Chunk, if_exists="skip")

    if table.rows() == 0:
        sample_chunks = [
            "Llamas are camelids known for their soft fur and use as pack animals.",
            "TiDB is a distributed SQL database for HTAP and AI workloads.",
            "Ollama enables local deployment of large language models.",
            "Kubernetes orchestrates containerized applications across clusters.",
            "Cybersecurity protects systems from digital attacks.",
        ]
        table.bulk_insert([Chunk(text=t) for t in sample_chunks])

    retrieved = (
        table.search(question)
        .distance_threshold(float(os.getenv("DISTANCE_THRESHOLD", "0.7")))
        .limit(int(os.getenv("RETRIEVE_LIMIT", "5")))
        .to_pydantic()
    )
    context = "\n\n".join([c.text for c in retrieved])

    prompt = PROMPT_TEMPLATE.format(question=question, context=context)

    resp = completion(
        api_base=OLLAMA_BASE_URL,
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    print(resp.choices[0].message.content or "")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
