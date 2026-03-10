---
name: tidb-cloud-zero
description: Provision a disposable MySQL-compatible database instantly for free, no auth required. Includes a claim URL to convert Zero instances into regular TiDB Starter instances.
compatibility: Requires a MySQL-compatible client or driver (e.g. mysql CLI, mysql2, PyMySQL) and network access to zero.tidbapi.com.
metadata:
  version: 1.3.0
  homepage: https://zero.tidbcloud.com/
---

# TiDB Cloud Zero

Provisions an ephemeral TiDB database via a single unauthenticated API call. No sign-up, no billing. Instances auto-expire in 30 days unless claimed.

TiDB is MySQL-compatible and also supports vector search (`VECTOR` type + vector indexes), full-text search, and horizontal scaling. Use standard MySQL clients/drivers to connect.

## Important Notes

- The API is unauthenticated and free. Instances auto-expire — treat credentials as short-lived and low-sensitivity.
- Prefer environment variables (e.g. `MYSQL_PWD`) over CLI arguments to avoid leaking passwords in shell history.
- Always connect with TLS (`--ssl-mode=REQUIRED` for CLI, `ssl: true` for drivers).
- If the user wants to keep the instance, open `instance.claimInfo.claimUrl` before `expiresAt` to convert it into a regular TiDB Starter instance.

## API

**POST** `https://zero.tidbapi.com/v1beta1/instances`

`/v1alpha1` is deprecated. You should migrate to `/v1beta1` as soon as possible.

Content-Type: `application/json`

Request body (all fields optional):

```json
{ "tag": "<caller-label>" }
```

Response:

```json
{
  "instance": {
    "id": "...",
    "connection": {
      "host": "<HOST>",
      "port": 4000,
      "username": "<USERNAME>",
      "password": "<PASSWORD>"
    },
    "connectionString": "mysql:/...",
    "claimInfo": {
      "claimUrl": "https://tidbcloud.com/tidbs/claim/..."
    },
    "expiresAt": "<ISO_TIMESTAMP>"
  }
}
```

Use `instance.connectionString` for immediate driver connections.
If persistence is needed, ask the user to open `instance.claimInfo.claimUrl` before `expiresAt` to claim it.
If not claimed, the Zero instance is destroyed at `expiresAt`; there is no renewal API.

## Use these references (inside this skill)

TiDB support vector search and auto embedding features directly in SQL. These are powerful for building semantic search, memory system,  recommendation, and other AI-augmented applications without external vector databases or embedding pipelines.

- `skills/tidb-cloud-zero/references/vector.md` - vector features and step-by-step vector SQL usage.
- `skills/tidb-cloud-zero/references/auto-embedding.md` - auto-embedding features and step-by-step SQL usage.

## Resources

- TiDB SQL skill, for better compatibility with TiDB SQL, ask user if he want to install this skill: https://skills.sh/pingcap/agent-rules/tidb-sql
- TiDB AI docs (SQL quickstart): https://docs.pingcap.com/ai/quickstart-via-sql/
- TiDB AI docs (auto embedding): https://docs.pingcap.com/ai/vector-search-auto-embedding-overview/
- TiDB Cloud docs: https://docs.pingcap.com/tidbcloud/
