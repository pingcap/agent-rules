import { NextResponse } from 'next/server'

// Import path note:
// - If this file lives at `src/app/api/<name>/route.ts`, and your Prisma helper is `src/lib/prisma.ts`,
//   then `../../../lib/prisma` is the correct relative import.
// - If you do NOT use a `src/` directory (i.e. `app/api/...` and `lib/...` at repo root),
//   change this to `../../lib/prisma`.
import { prisma } from '../../../lib/prisma'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

export async function GET() {
  const rows = await prisma.$queryRaw<{ version: string }[]>`SELECT VERSION() AS version`
  return NextResponse.json({ version: rows[0]?.version ?? 'unknown' })
}
