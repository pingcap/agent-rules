---
name: pytidb-sdk
description: Use for building or reviewing Python code that uses PyTiDB (TiDB Python AI SDK): connect with TiDBClient, define TableModel schemas, configure embeddings (EmbeddingFunction/VectorField/FullTextField), run vector/fulltext/hybrid search with filters, rerank, and convert results. Also use for transactions, raw SQL, image search, and MCP server integration in this repo.
---

# PyTiDB SDK Usage

Use this skill to guide coding tasks that integrate the PyTiDB SDK. Keep the flow small and code-first, and load references only when needed.

## Workflow

1. Confirm connection inputs and environment (host/port/user/pass/db or DATABASE_URL).
2. Decide schema shape and embedding mode (server-side auto embedding vs client-side embedding).
3. Define TableModel classes and create tables.
4. Insert or bulk insert data, then query/search with the correct search type.
5. Apply filters, rerank, and choose result shape (list, pydantic, pandas).
6. Use transactions or raw SQL only when table APIs are insufficient.

## Schema and embeddings

- Prefer TableModel + Field/VectorField/FullTextField for schema.
- For server-side embedding, configure provider credentials via TiDBClient before creating the VectorField.
- For client-side embedding or multi-modal embedding, set EmbeddingFunction with use_server=False or multimodal=True.
- Use examples in `references/examples.md` to match common patterns.

## Search

- Use vector search for semantic similarity, fulltext for keyword matching, hybrid to combine both.
- Always call `.limit(n)` before materializing results.
- Use prefilter for vector search when you need filters applied before ANN.
- Use rerankers only when you have a query string and a rerank field.

## Transactions and raw SQL

- Use `with tidb_client.session()` for multi-step transactional flows.
- Use `tidb_client.query()` and `tidb_client.execute()` for raw SQL; keep SQL TiDB-compatible.

## References

- API and patterns: `references/api.md`
- Example inventory: `references/examples.md`
- MCP server usage: `references/mcp.md`
