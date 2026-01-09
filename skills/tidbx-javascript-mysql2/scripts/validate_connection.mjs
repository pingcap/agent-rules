// Minimal TiDB connection smoke test for Node.js + mysql2 (promise API).
//
// Usage:
//   1) npm i mysql2 dotenv
//   2) Set DATABASE_URL or TIDB_* env vars (see ../SKILL.md)
//   3) node scripts/validate_connection.mjs

import { createConnection } from 'mysql2/promise'
import fs from 'node:fs'

try {
  await import('dotenv/config')
} catch {
  // dotenv is optional; environment variables may be provided by the runtime instead.
}

function buildOptionsFromEnv() {
  return {
    host: process.env.TIDB_HOST ?? '127.0.0.1',
    port: Number(process.env.TIDB_PORT ?? 4000),
    user: process.env.TIDB_USER ?? 'root',
    password: process.env.TIDB_PASSWORD ?? '',
    database: process.env.TIDB_DATABASE ?? 'test',
    ssl:
      process.env.TIDB_ENABLE_SSL === 'true'
        ? {
            minVersion: 'TLSv1.2',
            ca: process.env.TIDB_CA_PATH ? fs.readFileSync(process.env.TIDB_CA_PATH) : undefined,
          }
        : undefined,
  }
}

async function main() {
  const conn = process.env.DATABASE_URL
    ? await createConnection(process.env.DATABASE_URL)
    : await createConnection(buildOptionsFromEnv())

  try {
    const [[row]] = await conn.query('SELECT VERSION() AS tidb_version')
    console.log(`Connected. VERSION() = ${row.tidb_version}`)
  } finally {
    await conn.end()
  }
}

main().catch((err) => {
  console.error(`Failed to connect: ${err?.message ?? String(err)}`)
  process.exitCode = 1
})

