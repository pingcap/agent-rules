import os

from dotenv import load_dotenv

from pytidb import TiDBClient
from pytidb.embeddings import EmbeddingFunction
from pytidb.schema import TableModel, Field

load_dotenv()


def build_embedding_function() -> EmbeddingFunction:
    """
    Prefer OpenAI if OPENAI_API_KEY is set; otherwise use a TiDB Cloud free embedding model.
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        return EmbeddingFunction(
            model_name="openai/text-embedding-3-small",
            api_key=openai_key,
        )

    return EmbeddingFunction(
        model_name="tidbcloud_free/amazon/titan-embed-text-v2",
    )


print("=== Connect to TiDB ===")
db = TiDBClient.connect(
    host=os.getenv("TIDB_HOST"),
    port=int(os.getenv("TIDB_PORT", "4000")),
    username=os.getenv("TIDB_USERNAME"),
    password=os.getenv("TIDB_PASSWORD", ""),
    database=os.getenv("TIDB_DATABASE", "quickstart_example"),
    ensure_db=True,
)
print("Connected")

print("\n=== Create embedding function ===")
text_embed = build_embedding_function()
print(f"Embedding model: {text_embed.model_name}")


print("\n=== Create table ===")


class Chunk(TableModel, table=True):
    __tablename__ = "chunks"
    __table_args__ = {"extend_existing": True}

    id: int = Field(primary_key=True)
    text: str = Field()
    text_vec: list[float] = text_embed.VectorField(source_field="text")
    user_id: int = Field()


table = db.create_table(schema=Chunk, if_exists="skip")
print("Table ready")

print("\n=== Reset data (truncate) ===")
table.truncate()
print("Truncated")

print("\n=== Insert sample data ===")
table.bulk_insert(
    [
        Chunk(text="PyTiDB is a Python library for developers to connect to TiDB.", user_id=2),
        Chunk(text="LlamaIndex is a framework for building AI applications.", user_id=2),
        Chunk(
            text="TiDB is a distributed SQL database that supports HTAP and AI workloads.",
            user_id=3,
        ),
    ]
)
print("Inserted 3 rows")

print("\n=== Query data ===")
for row in table.query(limit=10).to_pydantic():
    print(f"ID: {row.id}, Text: {row.text}, User ID: {row.user_id}")

print("\n=== Semantic search ===")
results = table.search("A library for my artificial intelligence software").limit(3).to_list()
for r in results:
    print(
        f"ID: {r['id']}, Text: {r['text']}, User ID: {r['user_id']}, Distance: {r['_distance']}"
    )
