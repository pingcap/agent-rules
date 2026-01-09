// Minimal end-to-end TiDB quickstart for Node.js + mysqljs/mysql (callback API).
//
// Usage:
//   1) npm i mysql dotenv
//   2) Set DATABASE_URL or TIDB_* env vars (see ../SKILL.md)
//   3) node templates/quickstart.mjs

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
    console.log(`Connected (VERSION() = ${rows[0].tidb_version})`)

    await query(`
      CREATE TABLE IF NOT EXISTS players (
        id BIGINT PRIMARY KEY AUTO_INCREMENT,
        coins INT NOT NULL,
        goods INT NOT NULL
      )
    `)

    const insertOk = await query('INSERT INTO players (coins, goods) VALUES (?, ?)', [100, 100])
    const playerId = insertOk.insertId
    console.log(`Inserted player id=${playerId}`)

    const playerRows = await query('SELECT id, coins, goods FROM players WHERE id = ?', [playerId])
    console.log('Read player', playerRows[0])

    await query('UPDATE players SET coins = coins + ?, goods = goods + ? WHERE id = ?', [50, 50, playerId])
    console.log(`Updated player id=${playerId}`)

    await query('DELETE FROM players WHERE id = ?', [playerId])
    console.log(`Deleted player id=${playerId}`)
  } finally {
    await end()
  }
}

main().catch((err) => {
  console.error(err)
  process.exitCode = 1
})

