export interface PriceDataEntry {
  productId: string;
  competitorId: string;
  price: number;
  timestamp: string; // ISO string
  currency: string;
  source: string;
  metadata?: {
    [key: string]: any;
  };
}

export interface WebSocketMessage {
  type: 'PRICE_UPDATE' | 'ALERT_TRIGGERED';
  payload: {
    productId: string;
    competitorId: string;
    price: number;
    timestamp: string;
    message?: string;
    language?: 'en' | 'bn';
    [key: string]: any;
  };
}

export interface UserPreferences {
  mutedCompetitors: string[];
  language: 'en' | 'bn';
  alertsEnabled: boolean;
  chartPreferences: {
    showTrend: boolean;
    showAnnotations: boolean;
    showVolume: boolean;
  };
}

export interface PriceTrendData {
  [competitorId: string]: {
    label: string;
    data: PriceDataEntry[];
    metadata: {
      color: string;
      icon?: string;
      [key: string]: any;
    };
  };
}

export interface AlertMessage {
  id: string;
  productId: string;
  competitorId: string;
  message: string;
  timestamp: string;
  language: 'en' | 'bn';
  severity: 'info' | 'warning' | 'error';
  isRead: boolean;
}
