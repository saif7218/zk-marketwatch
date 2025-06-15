import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import { createServer } from 'http';
import { Server, WebSocket } from 'ws';
import dotenv from 'dotenv';
import { PrismaClient } from '@prisma/client';
import { WebSocketManager } from './utils/websocketManager';
import { Logger } from './utils/logger';
import { priceRouter } from './routes/price.routes';
import { competitorRouter } from './routes/competitor.routes';
import { monitorRouter } from './routes/monitor.routes';
import { agentsRouter } from './routes/agents';

dotenv.config();

const app = express();
const httpServer = createServer(app);
const wsServer = new Server({ server: httpServer });
const wsManager = WebSocketManager.getInstance(wsServer);

// Initialize Prisma client
const prisma = new PrismaClient();

// Middleware
app.use(cors());
app.use(helmet());
app.use(morgan('dev'));
app.use(express.json());

// Routes
app.use('/api/prices', priceRouter);
app.use('/api/competitors', competitorRouter);
app.use('/api/monitor', monitorRouter);

// Socket.io connection
// WebSocket connection handling
wsServer.on('connection', (ws: WebSocket) => {
  Logger.info('WebSocket client connected');

  ws.on('close', () => {
    Logger.info('WebSocket client disconnected');
  });
});

// Routes
app.use('/api/prices', priceRouter);
app.use('/api/competitors', competitorRouter);
app.use('/api/monitor', monitorRouter);
app.use('/api/agents', agentsRouter);

// Error handling middleware
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error(err.stack);
  res.status(500).json({ message: 'Something went wrong!' });
});

const PORT = process.env.PORT || 3001;

httpServer.listen(PORT, () => {
  Logger.info(`Server is running on port ${PORT}`);
  Logger.info(`WebSocket server initialized with ${wsManager.getClientCount()} clients`);
});
