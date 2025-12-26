# TiDB Cloud Serverless Driver Kysely Tutorial

Use `@tidbcloud/kysely` when you need HTTP-based connections for serverless or edge
runtimes. It improves reliability where TCP pools are not available.

## Prereqs

- Node.js 18+ and npm.
- A {{{ .starter }}} cluster.
- `DATABASE_URL` set to `mysql://[username]:[password]@[host]/[database]`.

## Node.js (serverless driver)

```bash
npm install kysely @tidbcloud/kysely @tidbcloud/serverless
```

```ts
import { Kysely, GeneratedAlways, Selectable } from 'kysely'
import { TiDBCloudServerlessDialect } from '@tidbcloud/kysely'

interface Database {
  person: PersonTable
}

interface PersonTable {
  id: GeneratedAlways<number>
  name: string
  gender: 'male' | 'female'
}

const db = new Kysely<Database>({
  dialect: new TiDBCloudServerlessDialect({ url: process.env.DATABASE_URL }),
})

type Person = Selectable<PersonTable>
export async function findPeople(criteria: Partial<Person> = {}) {
  let query = db.selectFrom('person')

  if (criteria.name) {
    query = query.where('name', '=', criteria.name)
  }

  return await query.selectAll().execute()
}

console.log(await findPeople())
```

## Edge (Vercel example)

```bash
npm install kysely @tidbcloud/kysely @tidbcloud/serverless
```

```ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { Kysely, GeneratedAlways, Selectable } from 'kysely'
import { TiDBCloudServerlessDialect } from '@tidbcloud/kysely'

export const runtime = 'edge'

interface Database {
  person: PersonTable
}

interface PersonTable {
  id: GeneratedAlways<number>
  name: string
  gender: 'male' | 'female' | 'other'
}

const db = new Kysely<Database>({
  dialect: new TiDBCloudServerlessDialect({ url: process.env.DATABASE_URL }),
})

type Person = Selectable<PersonTable>
async function findPeople(criteria: Partial<Person> = {}) {
  let query = db.selectFrom('person')

  if (criteria.name) {
    query = query.where('name', '=', criteria.name)
  }

  return await query.selectAll().execute()
}

export async function GET(request: NextRequest) {
  const query = request.nextUrl.searchParams.get('query')
  const response = query ? await findPeople({ name: query }) : await findPeople()
  return NextResponse.json(response)
}
```

## Links

- Kysely: https://kysely.dev/docs/intro
- @tidbcloud/kysely: https://github.com/tidbcloud/kysely
