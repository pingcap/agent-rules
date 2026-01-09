// Minimal Prisma ORM quickstart for TiDB (TypeScript).
//
// Setup:
//   1) npm i @prisma/client && npm i -D prisma typescript ts-node @types/node
//   2) npx prisma init
//   3) Set DATABASE_URL (see SKILL.md for TLS params)
//   4) Put a schema in prisma/schema.prisma (you can copy templates/schema.prisma)
//   5) npx prisma migrate dev
//
// Run:
//   npx ts-node templates/quickstart.ts

import type { Player } from '@prisma/client'
import { PrismaClient } from '@prisma/client'

async function getTiDBVersion(prisma: PrismaClient): Promise<string> {
  const rows = await prisma.$queryRaw<{ version: string }[]>`SELECT VERSION() AS version`
  return rows[0]?.version ?? 'unknown'
}

async function main(): Promise<void> {
  const prisma = new PrismaClient()
  try {
    const version = await getTiDBVersion(prisma)
    console.log(`Connected (VERSION() = ${version})`)

    const created: Player = await prisma.player.create({
      data: { name: 'Alice', coins: 100, goods: 100 },
    })
    console.log(`Inserted player id=${created.id}`)

    const got = await prisma.player.findUnique({ where: { id: created.id } })
    console.log('Read player', got)

    const updated: Player = await prisma.player.update({
      where: { id: created.id },
      data: { coins: { increment: 50 }, goods: { increment: 50 } },
    })
    console.log(`Updated player id=${updated.id}`)

    await prisma.player.delete({ where: { id: created.id } })
    console.log(`Deleted player id=${created.id}`)
  } finally {
    await prisma.$disconnect()
  }
}

main().catch((err: unknown) => {
  console.error(err)
  process.exitCode = 1
})

