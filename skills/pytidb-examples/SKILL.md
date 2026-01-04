---
name: pytidb-examples
description: Use when running or adapting PyTiDB example apps in /examples (quickstart, auto embedding, vector/fulltext/hybrid search, image search, memory, RAG, text2sql, realtime vector search). Covers setup, env vars, and which entry script to run.
---

# PyTiDB Examples Runner

Use this skill to run or adapt examples under `pytidb/examples`. Keep instructions aligned with each example README.

## Workflow

1. Pick the example folder and read its README first.
2. Create a virtualenv, install the example requirements file, and load env vars.
3. Run the example entry script (CLI or Streamlit) as documented.
4. If the example uses embeddings, confirm provider keys and models.

## Notes

- Examples use `.env` files for connection and API keys. Use placeholders and do not commit secrets.
- Streamlit examples default to http://localhost:8501.

## References

- Example catalog and entry points: `references/catalog.md`
