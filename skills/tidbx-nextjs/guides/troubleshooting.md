# Troubleshooting (Next.js + TiDB)

## "Edge runtime" errors / Node APIs missing

Symptoms:
- Errors about Node built-ins (`net`, `tls`, `fs`) or TCP sockets
- mysql2/Prisma fails in an Edge runtime

Fix:
- Ensure the code runs in Node.js runtime routes.
- For Route Handlers, export `runtime = 'nodejs'`.

If you must run on Edge-like runtimes, use `tidbx-serverless-driver` instead of TCP drivers.

## Leaking secrets to the browser

- Never put DB credentials in `NEXT_PUBLIC_*` env vars.
- Do not import DB client modules into Client Components (`'use client'`).

## Too many connections / connection errors on serverless

- Use a singleton/pool pattern (cache on `globalThis`) to reuse between invocations when possible.
- Keep pools small for serverless environments.

## Unexpected caching of API responses

- Ensure your Route Handler is dynamic if it reads fresh DB state.
- For GET handlers, you can export `dynamic = 'force-dynamic'` to avoid static caching.

