// Minimal end-to-end TiDB quickstart for Node.js + mysql2 (promise API).
//
// Usage:
//   1) npm i mysql2 dotenv
//   2) Set DATABASE_URL or TIDB_* env vars (see ../SKILL.md)
//   3) node templates/quickstart.mjs

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
    const [[ver]] = await conn.query('SELECT VERSION() AS tidb_version')
    console.log(`Connected (VERSION() = ${ver.tidb_version})`)

    await conn.execute(`
      CREATE TABLE IF NOT EXISTS players (
        id BIGINT PRIMARY KEY AUTO_INCREMENT,
        coins INT NOT NULL,
        goods INT NOT NULL
      )
    `)

    const [insertResult] = await conn.execute(
      'INSERT INTO players (coins, goods) VALUES (?, ?)',
      [100, 100],
    )
    const playerId = insertResult.insertId
    console.log(`Inserted player id=${playerId}`)

    const [[player]] = await conn.execute('SELECT id, coins, goods FROM players WHERE id = ?', [
      playerId,
    ])
    console.log(`Read player`, player)

    await conn.execute('UPDATE players SET coins = coins + ?, goods = goods + ? WHERE id = ?', [
      50,
      50,
      playerId,
    ])
    console.log(`Updated player id=${playerId}`)

    await conn.execute('DELETE FROM players WHERE id = ?', [playerId])
    console.log(`Deleted player id=${playerId}`)
  } finally {
    await conn.end()
  }
}

main().catch((err) => {
  console.error(err)
  process.exitCode = 1
})
