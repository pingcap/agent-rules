# PyTiDB SDK API Notes

## Core imports

```python
from pytidb import TiDBClient, Table
from pytidb.schema import TableModel, Field, FullTextField, DistanceMetric
from pytidb.embeddings import EmbeddingFunction
from pytidb.rerankers import Reranker, BaseReranker
```

## Connect

```python
tidb_client = TiDBClient.connect(
    host="localhost",
    port=4000,
    username="root",
    password="",
    database="test",
    ensure_db=True,
)
```

Alternative: pass a full URL and skip host/port.

## Define schema

Use TableModel + Field/VectorField/FullTextField.

```python
class Chunk(TableModel):
    __tablename__ = "chunks"
    id: int = Field(primary_key=True)
    text: str = FullTextField()
    text_vec: list[float] = EmbeddingFunction(
        "openai/text-embedding-3-small"
    ).VectorField(source_field="text")
```

If you need manual vectors, use a raw VECTOR column via sa_column.

## Embedding providers (server-side)

- Configure provider credentials before defining VectorField:

```python
tidb_client.configure_embedding_provider("openai", api_key=OPENAI_API_KEY)
```

- Common providers used in examples: tidbcloud_free, openai, jina_ai, cohere, huggingface, nvidia_nim, gemini.

## Table creation and data ops

```python
table = tidb_client.create_table(schema=Chunk, if_exists="overwrite")

# Inserts
row = table.insert(Chunk(id=1, text="foo"))
table.bulk_insert([Chunk(id=2, text="bar"), Chunk(id=3, text="baz")])

# Update/delete
table.update({"text": "updated"}, filters={"id": 1})
table.delete(filters={"id": {"$in": [2, 3]}})
```

## Search

```python
results = (
    table.search("query", search_type="vector")
    .distance_metric(DistanceMetric.COSINE)
    .filter({"user_id": {"$in": [1, 2]}}, prefilter=True)
    .limit(5)
    .to_list()
)
```

Search chain methods (common):
- `vector_column(name)`
- `text_column(name)`
- `distance_metric(metric)`
- `distance_threshold(max_dist)`
- `distance_range(min_dist, max_dist)`
- `num_candidate(n)`
- `filter(filters, prefilter=False)`
- `fusion(method=..., vs_weight=..., fts_weight=...)` (hybrid only)
- `rerank(reranker, rerank_field=None)`
- `limit(n)`

Hybrid search accepts a QueryBundle:

```python
query = {"query": "hello", "query_vector": [0.1, 0.2]}
results = table.search(query, search_type="hybrid").limit(5).to_list()
```

## Filters

Filters can be:
- Dict syntax
- Raw SQL string
- SQLAlchemy expressions

Dict operators:
- `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$in`, `$nin`, `$and`, `$or`

JSON field syntax: `{"meta.owner_id": {"$eq": 1}}`.

## Rerankers

```python
reranker = Reranker(model="cohere/rerank-english-v3.0")
results = (
    table.search("query")
    .rerank(reranker, rerank_field="text")
    .limit(10)
    .to_list()
)
```

## Result shapes

- `to_list()` returns list[dict] with `_distance` and `_score` for vector results.
- `to_pydantic()` returns model instances; similarity_score and score are available on vector results.
- `to_pandas()` requires `pytidb[pandas]`.

## Transactions and raw SQL

```python
with tidb_client.session() as session:
    tidb_client.execute("UPDATE players SET balance = balance - 10 WHERE id = 1")
    tidb_client.execute("UPDATE players SET balance = balance + 10 WHERE id = 2")
    session.commit()
```

Raw SQL query:

```python
rows = tidb_client.query("SELECT * FROM chunks").to_list()
```
