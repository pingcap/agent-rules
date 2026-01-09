import 'server-only'

import fs from 'node:fs'
import { createPool, type Pool } from 'mysql2/promise'

type GlobalWithTiDBPool = typeof globalThis & { __tidbPool?: Pool }

function createTiDBPool(): Pool {
  return createPool({
    host: process.env.TIDB_HOST,
    port: Number(process.env.TIDB_PORT ?? 4000),
    user: process.env.TIDB_USER,
    password: process.env.TIDB_PASSWORD,
    database: process.env.TIDB_DATABASE ?? 'test',
    ssl:
      process.env.TIDB_ENABLE_SSL === 'true'
        ? {
            minVersion: 'TLSv1.2',
            ca: process.env.TIDB_CA_PATH ? fs.readFileSync(process.env.TIDB_CA_PATH) : undefined,
          }
        : undefined,
    connectionLimit: Number(process.env.TIDB_CONNECTION_LIMIT ?? 1),
    maxIdle: Number(process.env.TIDB_MAX_IDLE ?? 1),
    // TiDB Cloud connections can be closed when idle; keep idle timeout <= 300s.
    idleTimeout: Number(process.env.TIDB_IDLE_TIMEOUT_MS ?? 300_000),
    enableKeepAlive: true,
  })
}

export function getTiDBPool(): Pool {
  const globalWithPool = globalThis as GlobalWithTiDBPool
  if (!globalWithPool.__tidbPool) {
    globalWithPool.__tidbPool = createTiDBPool()
  }
  return globalWithPool.__tidbPool
}
