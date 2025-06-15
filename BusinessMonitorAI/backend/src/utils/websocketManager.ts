import { Server, WebSocket } from 'ws';
import { Logger } from '../utils/logger';

export class WebSocketManager {
  private static instance: WebSocketManager;
  private server: Server;
  private clients: Set<WebSocket> = new Set();
  private isInitialized = false;

  private constructor(server: Server) {
    this.server = server;
    this.setupEventListeners();
  }

  public static getInstance(server: Server): WebSocketManager {
    if (!WebSocketManager.instance) {
      WebSocketManager.instance = new WebSocketManager(server);
    }
    return WebSocketManager.instance;
  }

  private setupEventListeners(): void {
    this.server.on('connection', (ws: WebSocket) => {
      this.clients.add(ws);
      
      ws.on('close', () => {
        this.clients.delete(ws);
      });

      ws.on('error', (error: Error) => {
        Logger.error('WebSocket error:', error);
        this.clients.delete(ws);
      });
    });

    this.server.on('error', (error: Error) => {
      Logger.error('WebSocket server error:', error);
    });
  }

  public broadcast(messageType: string, payload: any): void {
    const message = {
      type: messageType,
      payload,
      timestamp: new Date().toISOString()
    };

    const stringifiedMessage = JSON.stringify(message);

    this.clients.forEach((client: WebSocket) => {
      if (client.readyState === WebSocket.OPEN) {
        try {
          client.send(stringifiedMessage);
        } catch (error: Error) {
          Logger.error('Failed to send message to client:', error);
          this.clients.delete(client);
        }
      }
    });
  }

  public getClientCount(): number {
    return this.clients.size;
  }
}
