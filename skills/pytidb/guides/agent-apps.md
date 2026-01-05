# Agent-ish apps (RAG / memory / text2sql)

These are larger examples. Use them when you want an “AI app” that happens to store/search in TiDB via PyTiDB.

## RAG (retrieval-augmented generation)

- Template: `templates/rag.py`
- Uses: vector search retrieval + local LLM (Ollama via LiteLLM)
- Best for: offline-ish local demos where you control the model runtime

## Memory (persistent agent memory)

- Templates:
  - `templates/memory_lib.py`
  - `templates/memory.py`
- Uses: extract facts → store as vectors → retrieve by similarity per user_id

## Text2SQL

- Template: `templates/text2sql.py`
- Uses: OpenAI to generate SQL + executes on TiDB via PyTiDB
- Safety: always review generated SQL; block non-SELECT in app logic
