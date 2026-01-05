# Custom embedding function (PyTiDB)

PyTiDB supports **custom embedding functions** by implementing `BaseEmbeddingFunction`. This is useful when:
- you want to run embeddings locally (CPU/GPU),
- you want to use a model/provider not built into PyTiDB,
- you want full control over batching, timeouts, and preprocessing.

This guide summarizes a common pattern using **BGE-M3** as an example.

## Workflow checklist

- [ ] Pick an embedding model (example: BGE-M3)
- [ ] Implement `BaseEmbeddingFunction` methods
- [ ] Define a table with `embed_fn.VectorField(source_field=...)`
- [ ] Insert rows (auto embedding happens via your implementation)
- [ ] Search with `table.search(...)`

## Phase 1: Install dependencies

You need:
- `pytidb`
- an embedding runtime library (example: `FlagEmbedding` for BGE-M3)

Example:

```bash
pip install pytidb FlagEmbedding
```

Notes:
- The first run may download model files (network required).
- GPU usage depends on your environment and library support.

## Phase 2: Implement a custom embedding function

See `templates/custom_embedding_function.py`.

Key requirements:
- Set `dimensions` correctly (BGE-M3 is typically 1024).
- Implement:
  - `get_query_embedding(...)`
  - `get_source_embedding(...)`
  - `get_source_embeddings(...)` (batch)

## Phase 3: Use it with auto embedding

Define a table where the vector field is sourced from a text field:

```py
class Document(TableModel):
    id: int = Field(primary_key=True)
    content: str = Field()
    content_vec: list[float] = embed_fn.VectorField(source_field="content")
```

Then inserts automatically call your embedder for `content_vec`.

## Phase 4: Run a minimal example

See `templates/custom_embedding.py`.

## Troubleshooting

- **Dimension mismatch**: ensure `dimensions` matches what your model returns.
- **Slow first run**: model download/load can take minutes.
- **OOM (GPU/CPU)**: switch to CPU, disable FP16, reduce batch sizes.
