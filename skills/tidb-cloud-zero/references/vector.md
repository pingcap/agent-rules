---
title: TiDB Vector Search (Types, Functions, Indexes)
---

# TiDB Vector Search (Types, Functions, Indexes)

This reference explains what vector features TiDB provides, then shows how to use them with SQL.

## 1) What Is Available

Core objects:

- `VECTOR`: variable dimension vector column.
- `VECTOR(D)`: fixed dimension vector column (required for vector index).

Core functions:

- Distance: `VEC_COSINE_DISTANCE`, `VEC_L2_DISTANCE`, `VEC_L1_DISTANCE`, `VEC_NEGATIVE_INNER_PRODUCT`
- Parsing helpers: `VEC_FROM_TEXT`, `VEC_AS_TEXT`, `CAST(... AS VECTOR)`

Index and acceleration:

- HNSW vector index (`VECTOR INDEX` / `CREATE VECTOR INDEX`)
- TiFlash replica is required for vector index acceleration.

Typical query modes:

- Exact search: distance order over table scan.
- ANN TopK search: distance order + `LIMIT` with vector index.

## 2) How To Use

### Step 1: Create table

```sql
CREATE TABLE embedded_documents (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  content TEXT NOT NULL,
  embedding VECTOR(3)
);
```

### Step 2: Insert vectors

```sql
INSERT INTO embedded_documents (content, embedding) VALUES
  ('dog', '[1,2,1]'),
  ('fish', '[1,2,4]'),
  ('tree', '[1,0,0]');
```

### Step 3: Run exact TopK retrieval

```sql
SELECT id, content, VEC_COSINE_DISTANCE(embedding, '[1,2,3]') AS distance
FROM embedded_documents
ORDER BY distance
LIMIT 5;
```

### Step 4: (Optional) Add HNSW index for ANN

```sql
CREATE TABLE docs_with_index (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  content TEXT NOT NULL,
  embedding VECTOR(3),
  VECTOR INDEX idx_embedding ((VEC_COSINE_DISTANCE(embedding)))
);

CREATE VECTOR INDEX idx_embedding
ON docs_with_index ((VEC_COSINE_DISTANCE(embedding)))
USING HNSW;
```

### Step 5: Verify index usage

```sql
EXPLAIN SELECT id, content
FROM docs_with_index
ORDER BY VEC_COSINE_DISTANCE(embedding, '[1,2,3]')
LIMIT 10;

SHOW WARNINGS;
```

## 3) Common Pitfalls

- Index not used because query shape is not TopK (`ORDER BY ... ASC LIMIT K`).
- Index not used because function mismatch between DDL and query.
- Column uses `VECTOR` instead of `VECTOR(D)` for index scenarios.
- TiFlash replica is missing.
- Vector contains invalid values (`NaN`, `Inf`).

## 4) Source Docs

- https://docs.pingcap.com/ai/vector-search-data-types/
- https://docs.pingcap.com/ai/vector-search-functions-and-operators/
- https://docs.pingcap.com/ai/vector-search-index/
- https://docs.pingcap.com/tidbcloud/vector-search-limitations/
- https://docs.pingcap.com/ai/quickstart-via-sql/
