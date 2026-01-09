import 'server-only'

import { PrismaClient } from '@prisma/client'

type GlobalWithPrisma = typeof globalThis & { __prisma?: PrismaClient }

export const prisma: PrismaClient = (globalThis as GlobalWithPrisma).__prisma ?? new PrismaClient()

if (process.env.NODE_ENV !== 'production') {
  ;(globalThis as GlobalWithPrisma).__prisma = prisma
}

