# Quickstart (Next.js App Router + TiDB)

Goal: add a working backend-for-frontend API in `app/api/*/route.ts` that queries TiDB.

This guide defaults to Prisma (recommended) and also includes a mysql2 alternative.

## Phase 1: Create a Next.js project (TypeScript)

```bash
npx create-next-app@latest
```

Choose:
- App Router: yes
- TypeScript: yes

## Phase 2: Configure environment variables

For local development, put secrets in `.env.local` (do not commit it).

Pick one style:

- Prisma: `DATABASE_URL=...` (preferred)
- mysql2: `TIDB_HOST/TIDB_USER/...` (or `DATABASE_URL` if you want)

## Phase 3A (recommended): Prisma path

Follow `tidbx-prisma` to set up Prisma schema + migrations.

Then, add:

1) `src/lib/prisma.ts` from `templates/prisma-client.ts`  
2) `src/app/api/health/route.ts` from `templates/route-handler-prisma.ts`

Run:

```bash
npx prisma migrate dev
npm run dev
```

## Phase 3B (minimal demo): mysql2 path

Install:

```bash
npm i mysql2
```

Then, add:

1) `src/lib/tidb.ts` from `templates/tidb-mysql2-pool.ts`  
2) `src/app/api/health/route.ts` from `templates/route-handler-mysql2.ts`

Run:

```bash
npm run dev
```

## Phase 4: Deploy

- Set env vars in your hosting provider (e.g., Vercel Project Settings -> Environment Variables).
- Keep DB code server-only: route handlers, server actions, or server components.
