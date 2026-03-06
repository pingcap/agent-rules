---
name: tidbx-prisma
description: Prisma ORM setup and usage for TiDB from Node.js/TypeScript. Covers configuring prisma/schema.prisma (MySQL provider), DATABASE_URL formatting for TiDB Cloud TLS (sslaccept=strict and optional sslcert), migrations (prisma migrate), Prisma Client generation, CRUD patterns, and safe raw SQL ($queryRaw) plus runnable templates.
---

# TiDB Prisma Integration

Comprehensive Prisma ORM setup for TiDB with guided workflows.

## When to use this skill

- Set up Prisma in a new Node.js/TypeScript project
- Add Prisma to an existing project
- Define/modify models and run migrations
- Configure TiDB Cloud TLS correctly via `DATABASE_URL`
- Troubleshoot Prisma connection or migration issues

## Prisma vs drivers

Prisma is an ORM (models + migrations + typed client). If you only need a low-level MySQL driver, use:

- `tidbx-javascript-mysql2` (promise-native)
- `tidbx-javascript-mysqljs` (callback-based)

## Available guides

- `guides/quickstart.md` -- new project: install -> init -> migrate -> run TS quickstart
- `guides/troubleshooting.md` -- common TLS/connection/client-generation issues

I'll pick the smallest guide that matches your request, then use templates/scripts as needed.

## Quick examples

- "Add Prisma to my existing Node API and connect to TiDB Cloud" -> follow quickstart, then integrate client
- "My TiDB Cloud public endpoint fails with TLS errors" -> fix `DATABASE_URL` TLS params
- "Create tables from my Prisma models" -> run `prisma migrate dev`

## Reference: datasource config

In `prisma/schema.prisma`, use the MySQL connector and read `DATABASE_URL`:

```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "mysql"
  url      = env("DATABASE_URL")
}
```

## TLS notes for TiDB Cloud public endpoints

For TiDB Cloud public endpoints, configure TLS via query params in `DATABASE_URL`:

- Serverless/Starter/Essential (public endpoint): append `?sslaccept=strict`
- Dedicated (public endpoint with downloaded CA): append `?sslaccept=strict&sslcert=/absolute/path/to/ca.pem`

Examples:

```bash
DATABASE_URL='mysql://USER:PASSWORD@HOST:4000/DATABASE?sslaccept=strict'
DATABASE_URL='mysql://USER:PASSWORD@HOST:4000/DATABASE?sslaccept=strict&sslcert=/absolute/path/to/ca.pem'
```

## Install (TypeScript)

```bash
npm i @prisma/client
npm i -D prisma typescript ts-node @types/node
```

## Core patterns

### Create client and disconnect (always)

```ts
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()
try {
  // ... queries ...
} finally {
  await prisma.$disconnect()
}
```

### Safe raw SQL (parameterized)

- Prefer Prisma query builder when possible.
- When you need raw SQL, prefer `$queryRaw` with template literals (parameterized).
- Avoid `$queryRawUnsafe` unless you fully control the SQL.

```ts
const rows = await prisma.$queryRaw`SELECT VERSION() AS version`
```

## Templates & scripts

- `templates/schema.prisma` -- example schema (Player/Profile) mapped to TiDB tables
- `templates/quickstart.ts` -- minimal Prisma app: connect -> version -> CRUD (run with `ts-node`)
- `scripts/validate_connection.ts` -- connects and prints `SELECT VERSION()` (run with `ts-node`)

## Related skills

- `tidbx-nextjs` -- Next.js App Router integration patterns (route handlers, runtimes, deployment)
- `tidbx-kysely` -- typed query builder alternative to Prisma
- `tidbx-javascript-mysql2` -- low-level driver (promise API)
- `tidbx-javascript-mysqljs` -- low-level driver (callback API)

---

## Workflow

I will:
1. Confirm your runtime (Node) and project language (TypeScript)
2. Confirm your TiDB deployment (TiDB Cloud vs self-managed) and endpoint type
3. Choose a guide (`guides/quickstart.md` or `guides/troubleshooting.md`)
4. Generate the minimal Prisma files/commands to get you unblocked
