# Prisma + TiDB quickstart (TypeScript)

Goal: connect to TiDB via Prisma, run a migration, then do basic CRUD.

## Phase 1: Install deps

```bash
npm i @prisma/client
npm i -D prisma typescript ts-node @types/node
```

## Phase 2: Initialize Prisma

```bash
npx prisma init
```

Ensure `prisma/schema.prisma` uses:

- `datasource db { provider = "mysql" }`
- `url = env("DATABASE_URL")`

## Phase 3: Set DATABASE_URL (TLS when needed)

Use the TiDB Cloud "Connect" dialog to copy a connection string, then set:

- TiDB Cloud public endpoint: add `sslaccept=strict`
- TiDB Cloud public endpoint with downloaded CA: add `sslaccept=strict&sslcert=/absolute/path/to/ca.pem`

Examples:

```bash
DATABASE_URL='mysql://USER:PASSWORD@HOST:4000/DATABASE?sslaccept=strict'
DATABASE_URL='mysql://USER:PASSWORD@HOST:4000/DATABASE?sslaccept=strict&sslcert=/absolute/path/to/ca.pem'
```

## Phase 4: Define models

Copy `templates/schema.prisma` into `prisma/schema.prisma`, or define your own models.

## Phase 5: Run migrations (create tables)

```bash
npx prisma migrate dev
```

## Phase 6: Run the TypeScript quickstart

```bash
npx ts-node templates/quickstart.ts
```

