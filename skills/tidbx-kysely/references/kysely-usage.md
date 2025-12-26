# Kysely + TiDB Cloud usage

Use these snippets as starting points, and adjust exports if the package API differs.
`@tidbcloud/kysely` exposes a Kysely dialect for the TiDB Cloud serverless HTTP driver.

## Normal usage (TCP over mysql2) - default

```ts
import { Kysely, MysqlDialect } from 'kysely'
import { createPool } from 'mysql2'

interface Database {
  users: {
    id: number
    email: string
  }
}

const pool = createPool({
  uri: process.env.DATABASE_URL,
  connectionLimit: 10,
})

const db = new Kysely<Database>({
  dialect: new MysqlDialect({ pool }),
})

const users = await db.selectFrom('users').selectAll().execute()
console.log(users)

await db.destroy()
```

## Serverless usage (HTTP via @tidbcloud/kysely) - only for serverless/edge

Use the full tutorial in `references/serverless-kysely-tutorial.md` for setup and
step-by-step instructions in Node.js and edge environments.

## Install

TCP (standard Node server):

```bash
npm install kysely mysql2
```

Serverless/edge (HTTP):

```bash
npm install kysely @tidbcloud/kysely @tidbcloud/serverless
```

## Tips

- Use a `mysql://user:pass@host/db` URL in `DATABASE_URL`. Percent-encode special characters.
- Serverless/edge runtimes should avoid TCP pools and use the HTTP dialect.
