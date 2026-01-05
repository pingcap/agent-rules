# Search guide (vector vs full-text vs hybrid)

## When to use what

### Vector search

Use when you want semantic similarity (RAG retrieval, recommendations, dedup).

Typical setup:
- a `VectorField(...)` column (often auto-embedded from a text field)
- `table.search(query).limit(k)`
- optional metadata filters (JSON/scalar)

Start here:
- `templates/auto_embedding.py`
- `templates/vector_search.py`

### Full-text search

Use when keyword match matters (titles, product search, multilingual keyword queries).

Typical setup:
- a `FullTextField()` column
- `table.search("keywords", search_type="fulltext")`

Note:
- Full-text search availability can be limited by TiDB Cloud offering/region.

Minimal snippet:

```py
from pytidb.schema import TableModel, Field, FullTextField

class Item(TableModel):
    __tablename__ = "items"
    id: int = Field(primary_key=True)
    title: str = FullTextField()

# results = table.search("Bluetooth headphones", search_type="fulltext").limit(10).to_list()
```

### Hybrid search

Use when you want both:
- semantic similarity (vector) + keyword match (full-text)
- fused into one ranking (RRF/weighted), optionally reranked

Start here:
- `templates/hybrid_search.py`

## Common gotchas

- **Embedding dimension mismatch**: the stored vectors must match the field’s expected dimension.
- **Index/recall vs perf**: for vector search with filtering, adjust candidate count (`num_candidate`) and choose prefilter/postfilter intentionally.
- **Full-text support**: if you can’t create full-text indexes, check cluster feature availability/region.
