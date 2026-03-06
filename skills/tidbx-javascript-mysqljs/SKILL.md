---
name: tidbx-javascript-mysqljs
description: Connect to TiDB from JavaScript/Node.js using the mysqljs/mysql driver (npm package: mysql). Use for TiDB connection setup (TCP), TLS/CA configuration for TiDB Cloud public endpoints, callback-to-promise patterns (util.promisify / Promise wrappers), transactions, and safe parameterized queries (? placeholders) with small runnable connection/CRUD templates.
---

# TiDB + JavaScript (mysqljs/mysql)

Use this skill to connect to TiDB from Node.js with the `mysql` package (aka mysqljs/mysql), configure TLS correctly for TiDB Cloud, and provide small runnable snippets you can copy into a project.

## Important: mysql vs mysql2

These two drivers are easy to mix up:

- This skill is for **mysqljs/mysql** (`npm i mysql`) which is primarily callback-based.
- If you want the promise-native driver **mysql2** (`npm i mysql2` / `mysql2/promise`), jump to the `tidbx-javascript-mysql2` skill instead.

## Recommendation: prefer an ORM for app code

For most application code (models, migrations, types), prefer an ORM/query builder:

- Prisma ORM: use `tidbx-prisma`
- Kysely query builder: use `tidbx-kysely`

## When to use this skill

- Connect to TiDB from JavaScript/TypeScript (Node.js runtime) via `mysql` (mysqljs/mysql).
- Need TLS guidance (TiDB Cloud public endpoint) or CA certificate setup (TiDB Cloud Dedicated).
- Want a minimal "connect -> SELECT VERSION() -> CRUD" template using mysqljs/mysql.

## Code generation rules (Node.js)

- Never hardcode credentials; use `DATABASE_URL` or `TIDB_*` env vars.
- Use parameterized queries with `?` placeholders; never string-concatenate untrusted input.
- Prefer a pool for apps/services (`createPool`) and `pool.end()` on shutdown.
- mysqljs/mysql is callback-first; wrap callback APIs with `util.promisify` or small `new Promise(...)` helpers.

## Install

```bash
npm i mysql
```

If you want `.env` support:

```bash
npm i dotenv
```

## Minimal snippets

### Option A: connect with `DATABASE_URL` (recommended)

```js
import mysql from 'mysql'
import util from 'node:util'

const conn = mysql.createConnection(process.env.DATABASE_URL)
const query = util.promisify(conn.query).bind(conn)

const rows = await query('SELECT VERSION() AS v')
console.log(rows[0].v)
await util.promisify(conn.end).bind(conn)()
```

### Option B: connect with connection options (TLS / CA)

Use this when you want explicit TLS config (common for TiDB Cloud Dedicated with a downloaded CA).

```js
import mysql from 'mysql'
import fs from 'node:fs'

const conn = mysql.createConnection({
  host: process.env.TIDB_HOST,
  port: Number(process.env.TIDB_PORT ?? 4000),
  user: process.env.TIDB_USER,
  password: process.env.TIDB_PASSWORD,
  database: process.env.TIDB_DATABASE ?? 'test',
  ssl: process.env.TIDB_ENABLE_SSL === 'true'
    ? {
        minVersion: 'TLSv1.2',
        ca: process.env.TIDB_CA_PATH ? fs.readFileSync(process.env.TIDB_CA_PATH) : undefined,
      }
    : undefined,
})
```

Suggested env vars:

```bash
TIDB_HOST=...
TIDB_PORT=4000
TIDB_USER=...
TIDB_PASSWORD=...
TIDB_DATABASE=test
TIDB_ENABLE_SSL=true
# Optional (commonly used for TiDB Cloud Dedicated):
TIDB_CA_PATH=/absolute/path/to/ca.pem
```

## Transactions (mysqljs/mysql)

```js
import util from 'node:util'

const begin = util.promisify(conn.beginTransaction).bind(conn)
const commit = util.promisify(conn.commit).bind(conn)
const rollback = util.promisify(conn.rollback).bind(conn)
const query = util.promisify(conn.query).bind(conn)

try {
  await begin()
  await query('UPDATE players SET coins = coins + ? WHERE id = ?', [50, id])
  await commit()
} catch (e) {
  await rollback()
  throw e
}
```

## Templates & scripts in this skill

- `scripts/validate_connection.mjs` -- reads `DATABASE_URL` or `TIDB_*`, connects, prints `SELECT VERSION()`, then exits.
- `templates/quickstart.mjs` -- minimal end-to-end: connect -> create table -> insert -> query -> update -> delete.
