# TiDB Cloud Serverless Driver (Beta)

> **Note:** The serverless driver is in beta and only applies to Starter or Essential clusters.

## Why use it

Serverless and edge runtimes are short‑lived and often lack full TCP support. Traditional MySQL drivers expect long‑lived TCP connections, so they can fail or perform poorly. The TiDB Cloud serverless driver uses HTTP, which works well in serverless/edge environments while keeping a similar developer experience.

If you prefer REST over SQL/ORM, use Data Service (beta): https://docs.pingcap.com/tidbcloud/data-service-overview

## Install

```bash
npm install @tidbcloud/serverless
```

## Basic usage

### Query

```ts
import { connect } from '@tidbcloud/serverless'

const conn = connect({ url: 'mysql://[username]:[password]@[host]/[database]' })
const results = await conn.execute('select * from test where id = ?', [1])
```

### Transaction (experimental)

```ts
import { connect } from '@tidbcloud/serverless'

const conn = connect({ url: 'mysql://[username]:[password]@[host]/[database]' })
const tx = await conn.begin()

try {
  await tx.execute('insert into test values (1)')
  await tx.execute('select * from test')
  await tx.commit()
} catch (err) {
  await tx.rollback()
  throw err
}
```

## Edge examples

Vercel Edge Function:

```ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { connect } from '@tidbcloud/serverless'

export const runtime = 'edge'

export async function GET(request: NextRequest) {
  const conn = connect({ url: process.env.DATABASE_URL })
  const result = await conn.execute('show tables')
  return NextResponse.json({ result })
}
```

Cloudflare Workers:

```ts
import { connect } from '@tidbcloud/serverless'

export interface Env {
  DATABASE_URL: string
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const conn = connect({ url: env.DATABASE_URL })
    const result = await conn.execute('show tables')
    return new Response(JSON.stringify(result))
  }
}
```

Netlify Edge Function:

```ts
import { connect } from 'https://esm.sh/@tidbcloud/serverless'

export default async () => {
  const conn = connect({ url: Netlify.env.get('DATABASE_URL') })
  const result = await conn.execute('show tables')
  return new Response(JSON.stringify(result))
}
```

Deno:

```ts
import { connect } from 'npm:@tidbcloud/serverless'

const conn = connect({ url: Deno.env.get('DATABASE_URL') })
const result = await conn.execute('show tables')
```

Bun:

```ts
import { connect } from '@tidbcloud/serverless'

const conn = connect({ url: Bun.env.DATABASE_URL })
const result = await conn.execute('show tables')
```

## Configuration (essentials)

Connection‑level options:

- `url`: `mysql://[username]:[password]@[host]/[database]` (preferred)
- `fetch`: custom fetch (e.g., `undici` in Node.js)
- `arrayMode`: return rows as arrays
- `fullResult`: return full result object
- `decoders`: custom per‑column type decoders

SQL‑level options (override connection level):

- `arrayMode`, `fullResult`, `decoders`
- `isolation`: `READ COMMITTED` or `REPEATABLE READ` (only for `begin`)

URL encoding note: percent‑encode special characters in username/password/database. Example: `password1@//?` → `password1%40%2F%2F%3F`.

`url` replaces separate `host`, `username`, `password`, `database` fields.

## Features

Supported SQL: `SELECT`, `SHOW`, `EXPLAIN`, `USE`, `INSERT`, `UPDATE`, `DELETE`, `BEGIN`, `COMMIT`, `ROLLBACK`, `SET`, plus DDL.

Data type mapping (summary):

- Numeric types → `number`
- `BIGINT`, `DECIMAL` → `string`
- Binary/blob/bit → `Uint8Array`
- `JSON` → `object`
- `DATETIME`, `TIMESTAMP`, `DATE`, `TIME` → `string`

Use `utf8mb4` for correct string decoding. Since v0.1.0, binary/blob/bit types return `Uint8Array` (not `string`).

## Pricing

The driver is free. Usage consumes Request Units (RUs) and storage:

- Starter pricing: https://www.pingcap.com/tidb-cloud-starter-pricing-details/
- Essential pricing: https://www.pingcap.com/tidb-cloud-essential-pricing-details/

## Limitations

- Max 10,000 rows per query.
- One SQL statement per query.
- Private endpoints not supported.
- CORS blocks unauthorized browser origins; use from backend services only.
