import os

import dotenv

from pytidb import TiDBClient
from pytidb.datatype import JSON, TEXT
from pytidb.schema import TableModel, Field, VectorField

dotenv.load_dotenv()

# Connect to database with connection parameters
db = TiDBClient.connect(
    host=os.getenv("TIDB_HOST", "localhost"),
    port=int(os.getenv("TIDB_PORT", "4000")),
    username=os.getenv("TIDB_USERNAME", "root"),
    password=os.getenv("TIDB_PASSWORD", ""),
    database=os.getenv("TIDB_DATABASE", "basic_example"),
    ensure_db=True,
)

# Or connect with a connection string:
# db = TiDBClient.connect(database_url=os.getenv("TIDB_DATABASE_URL"))

print("=== CRUD: CREATE TABLE ===")


class Item(TableModel):
    __tablename__ = "items_in_basic_example"
    __table_args__ = {"extend_existing": True}

    id: int = Field(primary_key=True)
    content: str = Field(sa_type=TEXT)
    embedding: list[float] = VectorField(dimensions=3)
    meta: dict = Field(sa_type=JSON, default_factory=dict)


table = db.create_table(schema=Item, if_exists="skip")
print("Table ready")

print("\n=== TRUNCATE TABLE ===")
table.truncate()
print("Table truncated")

print("\n=== CREATE ===")
table.insert(
    Item(
        id=1,
        content="TiDB is a distributed SQL database",
        embedding=[0.1, 0.2, 0.3],
        meta={"category": "database"},
    )
)
table.bulk_insert(
    [
        Item(
            id=2,
            content="GPT-4 is a large language model",
            embedding=[0.4, 0.5, 0.6],
            meta={"category": "llm"},
        ),
        Item(
            id=3,
            content="LlamaIndex is a Python library for building AI-powered applications",
            embedding=[0.7, 0.8, 0.9],
            meta={"category": "rag"},
        ),
    ]
)
print("Created 3 items")

print("\n=== READ ===")
for item in table.query(limit=10).to_pydantic():
    print(f"ID: {item.id}, Content: {item.content}, Meta: {item.meta}")

print("\n=== UPDATE ===")
table.update(
    values={
        "content": "TiDB Cloud Starter is a fully-managed, auto-scaling cloud database service",
        "embedding": [0.1, 0.2, 0.4],
        "meta": {"category": "updated"},
    },
    filters={"id": 1},
)
updated = table.query(filters={"id": 1}).to_pydantic()[0]
print(f"Updated item #1 -> {updated.content} / {updated.meta}")

print("\n=== DELETE ===")
table.delete(filters={"id": 2})
print("Deleted item #2")

print("\n=== FINAL STATE ===")
for item in table.query(limit=10).to_pydantic():
    print(f"ID: {item.id}, Content: {item.content}, Meta: {item.meta}")

print("\n=== COUNT ROWS ===")
print(f"Rows: {table.rows()}")

print("\n=== DROP TABLE ===")
db.drop_table("items_in_basic_example")
print("Table dropped")
