---
title: TiDB Auto Embedding (Models, SQL Functions, Usage)
---

# TiDB Auto Embedding (Models, SQL Functions, Usage)

This reference explains what auto-embedding features are available, then shows how to use them with SQL.

## 1) What Is Available

Core capability:

- Convert text to embeddings directly in SQL via `EMBED_TEXT`.
- Run text-to-vector semantic retrieval via `VEC_EMBED_COSINE_DISTANCE` / `VEC_EMBED_L2_DISTANCE`.

Model choices:

- Hosted model example: `tidbcloud_free/amazon/titan-embed-text-v2` (1024 dimensions).
- BYOK providers are supported through TiDB global variables (for example OpenAI, Cohere).

Storage and query pattern:

- Use a generated stored vector column: `VECTOR(D) GENERATED ALWAYS AS (EMBED_TEXT(...)) STORED`.
- Optional HNSW vector index can accelerate retrieval.

Availability note:

- Auto embedding is documented for TiDB Cloud Starter (AWS).
- In unknown environments (including Zero), run a probe SQL first and then proceed if supported.

## 2) How To Use

### Step 1: Probe capability

```sql
SELECT EMBED_TEXT("tidbcloud_free/amazon/titan-embed-text-v2", "pingcap");
```

### Step 2: Create table with generated embedding column

```sql
CREATE TABLE docs_auto_embed (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  content TEXT NOT NULL,
  content_vec VECTOR(1024) GENERATED ALWAYS AS (
    EMBED_TEXT("tidbcloud_free/amazon/titan-embed-text-v2", content)
  ) STORED
);
```

### Step 3: Insert source text only

```sql
INSERT INTO docs_auto_embed (content) VALUES
  ('Electric vehicles reduce air pollution in cities.'),
  ('Solar panels convert sunlight into renewable energy.'),
  ('Plant-based diets lower carbon footprints.');
```

### Step 4: Query by natural language

```sql
SELECT id, content
FROM docs_auto_embed
ORDER BY VEC_EMBED_COSINE_DISTANCE(
  content_vec,
  'Renewable energy solutions for environmental protection'
)
LIMIT 3;
```

### Step 5: (Optional) Add vector index

```sql
CREATE VECTOR INDEX idx_content_vec
ON docs_auto_embed ((VEC_COSINE_DISTANCE(content_vec)))
USING HNSW;
```

## 3) BYOK and Provider Options

Set API keys when using BYOK models:

```sql
SET @@GLOBAL.TIDB_EXP_EMBED_OPENAI_API_KEY = "<OPENAI_API_KEY>";
SET @@GLOBAL.TIDB_EXP_EMBED_COHERE_API_KEY = "<COHERE_API_KEY>";
```

For some Cohere models, pass `options` such as `input_type`:

```sql
SELECT EMBED_TEXT(
  "cohere/embed-multilingual-v3.0",
  "There are many ways to use auto embedding",
  '{"input_type":"search_document"}'
);
```

## 4) Common Pitfalls

- `VECTOR(D)` dimension does not match model output dimension.
- Environment does not support auto embedding.
- Missing BYOK API key for selected provider.
- Index query shape does not satisfy TopK pattern.

## 5) Source Docs

- https://docs.pingcap.com/ai/vector-search-auto-embedding-overview/
- https://docs.pingcap.com/ai/vector-search-auto-embedding-overview#auto-embedding-functions
- https://docs.pingcap.com/ai/quickstart-via-sql/
- https://docs.pingcap.com/ai/vector-search-auto-embedding-openai/
- https://docs.pingcap.com/ai/vector-search-auto-embedding-cohere/
- https://docs.pingcap.com/ai/embedding-openai-compatible/
- https://docs.pingcap.com/ai/vector-search-auto-embedding-jina-ai/
- https://docs.pingcap.com/ai/vector-search-auto-embedding-gemini/
- https://docs.pingcap.com/ai/vector-search-auto-embedding-huggingface/
- https://docs.pingcap.com/ai/vector-search-auto-embedding-nvidia-nim/
- https://docs.pingcap.com/ai/vector-search-auto-embedding-amazon-titan/
