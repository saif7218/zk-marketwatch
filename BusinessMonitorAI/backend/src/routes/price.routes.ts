import { Router } from 'express';
import { prisma } from '../db';
import { z } from 'zod';
import { validateRequest } from '../middleware/validateRequest';

const router = Router();

// Price history schema
const priceHistorySchema = z.object({
  monitorId: z.string(),
  price: z.number(),
  change: z.number().optional(),
  changeType: z.enum(['INCREASE', 'DECREASE']).optional()
});

// Get price history for a monitor
router.get('/:monitorId/history', async (req, res) => {
  const { monitorId } = req.params;
  
  try {
    const priceHistory = await prisma.priceHistory.findMany({
      where: { monitorId },
      orderBy: { timestamp: 'desc' },
      include: { monitor: true }
    });
    
    res.json(priceHistory);
  } catch (error) {
    res.status(500).json({ message: 'Failed to fetch price history' });
  }
});

// Add new price record
router.post('/record', validateRequest(priceHistorySchema), async (req, res) => {
  const { monitorId, price, change, changeType } = req.body;
  
  try {
    const priceRecord = await prisma.priceHistory.create({
      data: {
        monitorId,
        price,
        change,
        changeType: changeType as any,
        timestamp: new Date()
      }
    });
    
    // Emit WebSocket event
    req.app.get('io').to(`monitor_${monitorId}`).emit('price_update', priceRecord);
    
    res.status(201).json(priceRecord);
  } catch (error) {
    res.status(500).json({ message: 'Failed to record price' });
  }
});

// Get price statistics
router.get('/:monitorId/stats', async (req, res) => {
  const { monitorId } = req.params;
  
  try {
    const stats = await prisma.priceHistory.aggregate({
      where: { monitorId },
      _avg: { price: true },
      _min: { price: true },
      _max: { price: true },
      _count: true
    });
    
    res.json(stats);
  } catch (error) {
    res.status(500).json({ message: 'Failed to fetch price statistics' });
  }
});

export { router as priceRouter };
