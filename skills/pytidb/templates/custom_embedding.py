import os

import dotenv

from pytidb import TiDBClient
from pytidb.datatype import TEXT
from pytidb.schema import TableModel, Field

from custom_embedding_function import BGEM3EmbeddingFunction

dotenv.load_dotenv()

db = TiDBClient.connect(
    host=os.getenv("TIDB_HOST", "localhost"),
    port=int(os.getenv("TIDB_PORT", "4000")),
    username=os.getenv("TIDB_USERNAME", "root"),
    password=os.getenv("TIDB_PASSWORD", ""),
    database=os.getenv("TIDB_DATABASE", "custom_embedding_example"),
    ensure_db=True,
)

embed_fn = BGEM3EmbeddingFunction()


class Document(TableModel):
    __tablename__ = "bge_m3_documents"
    __table_args__ = {"extend_existing": True}

    id: int = Field(primary_key=True)
    title: str = Field(sa_type=TEXT)
    content: str = Field(sa_type=TEXT)
    content_vec: list[float] = embed_fn.VectorField(source_field="content")


table = db.create_table(schema=Document, if_exists="skip")

if table.rows() == 0:
    table.bulk_insert(
        [
            Document(
                id=1,
                title="TiDB Introduction",
                content="TiDB is a distributed SQL database that supports OLTP and OLAP workloads.",
            ),
            Document(
                id=2,
                title="Vector Databases",
                content="Vector databases store and query high-dimensional vectors efficiently for semantic search.",
            ),
            Document(
                id=3,
                title="BGE-M3",
                content="BGE-M3 is an embedding model commonly used for dense retrieval.",
            ),
        ]
    )

results = table.search("Is TiDB a distributed database?").limit(3).to_list()
for r in results:
    print(r["title"], r["_distance"])
