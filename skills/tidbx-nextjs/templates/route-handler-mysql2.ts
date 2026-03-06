import { NextResponse } from 'next/server'

// Import path note:
// - If this file lives at `src/app/api/<name>/route.ts`, and your pool helper is `src/lib/tidb.ts`,
//   then `../../../lib/tidb` is the correct relative import.
// - If you do NOT use a `src/` directory (i.e. `app/api/...` and `lib/...` at repo root),
//   change this to `../../lib/tidb`.
import { getTiDBPool } from '../../../lib/tidb'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

export async function GET() {
  const pool = getTiDBPool()
  const [rows] = await pool.query('SELECT VERSION() AS tidb_version')
  return NextResponse.json({ rows })
}
