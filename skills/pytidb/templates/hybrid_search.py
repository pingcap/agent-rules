import json
import os

import dotenv

from pytidb import TiDBClient
from pytidb.embeddings import EmbeddingFunction
from pytidb.schema import FullTextField, TableModel, Field

dotenv.load_dotenv()

print("=== CONNECT TO TIDB ===")
db = TiDBClient.connect(
    host=os.getenv("TIDB_HOST", "localhost"),
    port=int(os.getenv("TIDB_PORT", "4000")),
    username=os.getenv("TIDB_USERNAME", "root"),
    password=os.getenv("TIDB_PASSWORD", ""),
    database=os.getenv("TIDB_DATABASE", "hybrid_search_example"),
    ensure_db=True,
)
print("Connected\n")

embed_fn = EmbeddingFunction(
    model_name="openai/text-embedding-3-small",
    api_key=os.getenv("OPENAI_API_KEY"),
)

print("=== CREATE TABLE ===")


class Chunk(TableModel, table=True):
    __tablename__ = "chunks"
    __table_args__ = {"extend_existing": True}

    id: int = Field(primary_key=True)
    text: str = FullTextField()
    text_vec: list[float] = embed_fn.VectorField(source_field="text")


table = db.create_table(schema=Chunk, if_exists="skip")
print("Table ready\n")

if table.rows() == 0:
    print("=== INSERT SAMPLE DATA ===")
    table.bulk_insert(
        [
            Chunk(text="TiDB is a distributed database that supports OLTP, OLAP, HTAP and AI workloads."),
            Chunk(text="PyTiDB is a Python library for developers to connect to TiDB."),
            Chunk(text="LlamaIndex is a Python library for building AI-powered applications."),
        ]
    )
    print("Inserted 3 rows\n")

print("=== PERFORM HYBRID SEARCH ===")
results = table.search("AI database", search_type="hybrid").limit(3).to_list()
for item in results:
    item.pop("text_vec", None)
print(json.dumps(results, indent=2, ensure_ascii=False))
