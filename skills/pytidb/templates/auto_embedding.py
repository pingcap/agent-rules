import os

import dotenv

from pytidb import TiDBClient
from pytidb.datatype import TEXT
from pytidb.embeddings import EmbeddingFunction
from pytidb.schema import TableModel, Field

dotenv.load_dotenv()

tidb_client = TiDBClient.connect(
    host=os.getenv("TIDB_HOST", "localhost"),
    port=int(os.getenv("TIDB_PORT", "4000")),
    username=os.getenv("TIDB_USERNAME", "root"),
    password=os.getenv("TIDB_PASSWORD", ""),
    database=os.getenv("TIDB_DATABASE", "auto_embedding_example"),
    ensure_db=True,
)

print("=== Auto embedding: define embedding function ===")

provider = os.getenv("EMBEDDING_PROVIDER", "tidbcloud_free")

if provider == "tidbcloud_free":
    embed_func = EmbeddingFunction(
        model_name="tidbcloud_free/amazon/titan-embed-text-v2",
    )
elif provider == "openai":
    tidb_client.configure_embedding_provider(
        provider="openai",
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    embed_func = EmbeddingFunction(
        model_name="openai/text-embedding-3-small",
    )
elif provider == "jina_ai":
    tidb_client.configure_embedding_provider(
        provider="jina_ai",
        api_key=os.getenv("JINA_AI_API_KEY"),
    )
    embed_func = EmbeddingFunction(
        model_name="jina_ai/jina-embeddings-v3",
    )
else:
    raise ValueError(f"Unsupported EMBEDDING_PROVIDER: {provider}")

print(f"Embedding model: {embed_func.model_name}")

print("\n=== Define table schema ===")


class Chunk(TableModel):
    __tablename__ = "chunks"
    __table_args__ = {"extend_existing": True}

    id: int = Field(primary_key=True)
    text: str = Field(sa_type=TEXT)
    text_vec: list[float] = embed_func.VectorField(source_field="text")


table = tidb_client.create_table(schema=Chunk, if_exists="skip")
print("Table ready")

print("\n=== Reset data (truncate) ===")
table.truncate()
print("Truncated")

print("\n=== Insert sample data (auto embedding) ===")
table.bulk_insert(
    [
        Chunk(text="TiDB is a distributed database that supports OLTP, OLAP, HTAP and AI workloads."),
        Chunk(text="PyTiDB is a Python library for developers to connect to TiDB."),
        Chunk(text="LlamaIndex is a Python library for building AI-powered applications."),
    ]
)
print("Inserted 3 rows")

print("\n=== Vector search (query auto embedded) ===")
results = table.search("HTAP database").limit(3).to_list()
for item in results:
    print(f"id: {item['id']}, text: {item['text']}, distance: {item['_distance']}")
