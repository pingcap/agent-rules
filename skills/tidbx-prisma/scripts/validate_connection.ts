// Prisma ORM TiDB connection smoke test (TypeScript).
//
// Prereqs:
//   - DATABASE_URL is set
//   - Prisma Client is generated (run: npx prisma generate OR npx prisma migrate dev)
//
// Run:
//   npx ts-node scripts/validate_connection.ts

import { PrismaClient } from '@prisma/client'

async function main(): Promise<void> {
  const prisma = new PrismaClient()
  try {
    const rows = await prisma.$queryRaw<{ version: string }[]>`SELECT VERSION() AS version`
    console.log(`Connected. VERSION() = ${rows[0]?.version ?? 'unknown'}`)
  } finally {
    await prisma.$disconnect()
  }
}

main().catch((err: unknown) => {
  const message = err instanceof Error ? err.message : String(err)
  console.error(`Failed to connect: ${message}`)
  process.exitCode = 1
})

