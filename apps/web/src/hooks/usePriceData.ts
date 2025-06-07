import { useEffect, useState, useRef, useMemo } from 'react';
import { useWebSocket } from './useWebSocket';
import { PriceDataEntry, WebSocketMessage, UserPreferences } from '../types/price';
import { useUserPreferences } from './useUserPreferences';

interface PriceHistoryResponse {
  data: PriceDataEntry[];
  metadata: {
    total: number;
    lastUpdated: string;
  };
}

export const usePriceData = (productId: string) => {
  const [priceData, setPriceData] = useState<PriceDataEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { preferences } = useUserPreferences();
  const wsRef = useRef<WebSocket | null>(null);

  // Fetch initial historical data
  useEffect(() => {
    const fetchHistoricalData = async () => {
      try {
        const response = await fetch(`/api/prices/history?product_id=${productId}`);
        if (!response.ok) throw new Error('Failed to fetch historical data');
        const data: PriceHistoryResponse = await response.json();
        
        // Sort by timestamp and apply preferences
        const filteredData = data.data
          .filter(item => !preferences.mutedCompetitors.includes(item.competitorId))
          .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
        
        setPriceData(filteredData);
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
        setLoading(false);
      }
    };

    fetchHistoricalData();
  }, [productId, preferences.mutedCompetitors]);

  // WebSocket connection for real-time updates
  const onMessage = (message: WebSocketMessage) => {
    if (message.type === 'PRICE_UPDATE' && message.payload.productId === productId) {
      const newEntry: PriceDataEntry = {
        productId: message.payload.productId,
        competitorId: message.payload.competitorId,
        price: message.payload.price,
        timestamp: message.payload.timestamp,
        currency: 'BDT', // Default currency
        source: 'real-time',
      };

      // Update state with new price data
      setPriceData(prevData => {
        // Remove duplicates and add new entry
        const existingIndex = prevData.findIndex(
          item => item.productId === productId && 
                 item.competitorId === message.payload.competitorId &&
                 item.timestamp === message.payload.timestamp
        );

        if (existingIndex !== -1) {
          // Update existing entry if it exists
          const newData = [...prevData];
          newData[existingIndex] = newEntry;
          return newData;
        }

        // Add new entry to the end
        return [...prevData, newEntry];
      });
    }
  };

  // WebSocket connection
  const { connect, disconnect } = useWebSocket(onMessage);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  // Memoized filtered data based on preferences
  const filteredData = useMemo(() => {
    return priceData.filter(item => !preferences.mutedCompetitors.includes(item.competitorId));
  }, [priceData, preferences.mutedCompetitors]);

  // Memoized price trend data for chart
  const priceTrendData = useMemo(() => {
    const groupedData: Record<string, PriceDataEntry[]> = {};
    filteredData.forEach(item => {
      if (!groupedData[item.competitorId]) {
        groupedData[item.competitorId] = [];
      }
      groupedData[item.competitorId].push(item);
    });

    return Object.entries(groupedData).map(([competitorId, data]) => ({
      competitorId,
      data: data.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()),
      latestPrice: data[data.length - 1]?.price || 0,
      priceChange: data.length > 1 ? ((data[data.length - 1].price - data[0].price) / data[0].price) * 100 : 0
    }));
  }, [filteredData]);

  return {
    data: filteredData,
    priceTrendData,
    loading,
    error,
    connect,
    disconnect
  };
};
