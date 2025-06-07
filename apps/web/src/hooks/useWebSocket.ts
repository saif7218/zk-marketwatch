import { useEffect, useRef, useCallback } from 'react';
import { WebSocketMessage } from '../types/price';
import { useUserPreferences } from './useUserPreferences';

interface WebSocketConfig {
  url: string;
  onMessage: (message: WebSocketMessage) => void;
  onError?: (error: Error) => void;
  onOpen?: () => void;
  onClose?: () => void;
}

export const useWebSocket = (
  onMessage: (message: WebSocketMessage) => void,
  onError?: (error: Error) => void,
  onOpen?: () => void,
  onClose?: () => void
) => {
  const { preferences } = useUserPreferences();
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  const reconnectDelay = 3000; // 3 seconds

  const connect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
    }

    const ws = new WebSocket(process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/monitor');

    ws.onopen = () => {
      reconnectAttempts.current = 0;
      if (onOpen) onOpen();
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.type === 'PRICE_UPDATE' || 
            (message.type === 'ALERT_TRIGGERED' && preferences.alertsEnabled)) {
          onMessage(message);
        }
      } catch (error) {
        if (onError) onError(error instanceof Error ? error : new Error('Invalid WebSocket message'));
      }
    };

    ws.onerror = (error) => {
      if (onError) onError(error instanceof Error ? error : new Error('WebSocket error'));
    };

    ws.onclose = () => {
      if (onClose) onClose();
      if (reconnectAttempts.current < maxReconnectAttempts) {
        setTimeout(() => {
          reconnectAttempts.current++;
          connect();
        }, reconnectDelay);
      }
    };

    wsRef.current = ws;
  }, [onMessage, onError, onOpen, onClose, preferences.alertsEnabled]);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return { connect, disconnect };
};
