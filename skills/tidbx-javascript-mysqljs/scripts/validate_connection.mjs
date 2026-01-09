// Minimal TiDB connection smoke test for Node.js + mysqljs/mysql (callback API).
//
// Usage:
//   1) npm i mysql dotenv
//   2) Set DATABASE_URL or TIDB_* env vars (see ../SKILL.md)
//   3) node scripts/validate_connection.mjs

import mysql from 'mysql'
import fs from 'node:fs'
import util from 'node:util'

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
    ? mysql.createConnection(process.env.DATABASE_URL)
    : mysql.createConnection(buildOptionsFromEnv())

  const query = util.promisify(conn.query).bind(conn)
  const end = util.promisify(conn.end).bind(conn)

  try {
    const rows = await query('SELECT VERSION() AS tidb_version')
    console.log(`Connected. VERSION() = ${rows[0].tidb_version}`)
  } finally {
    await end()
  }
}

main().catch((err) => {
  console.error(`Failed to connect: ${err?.message ?? String(err)}`)
  process.exitCode = 1
})

