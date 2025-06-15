import { PrismaClient } from '@prisma/client';

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

export const prisma = globalForPrisma.prisma ?? new PrismaClient();

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;

// Add a graceful shutdown hook
process.on('SIGTERM', () => {
  prisma.$disconnect();
});

process.on('SIGINT', () => {
  prisma.$disconnect();
});
