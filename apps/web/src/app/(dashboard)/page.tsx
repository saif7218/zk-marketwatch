import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";
import { AlertCircle, Loader2 } from "lucide-react";
import { useTranslation } from "react-i18next";
import dynamic from 'next/dynamic';
import Settings from "./settings";
import { AlertMessage } from "@/types/price";
import WebsiteMonitor from "@/components/WebsiteMonitor";

// Dynamically import the PriceTrendChart to avoid SSR issues with charts
const PriceTrendChart = dynamic(
  () => import('@/components/PriceTrendChart'),
  { ssr: false }
);

// Mock hook for price data - replace with real implementation
const usePriceData = (productId: string) => {
  const [data, setData] = React.useState<any[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<Error | null>(null);

  React.useEffect(() => {
    // Simulate API call
    const fetchData = async () => {
      try {
        setLoading(true);
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        // Mock data
        const mockData = [
          {
            competitorId: 'competitor-1',
            data: Array.from({ length: 7 }, (_, i) => ({
              timestamp: new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000).toISOString(),
              price: 100 + Math.random() * 20
            }))
          },
          {
            competitorId: 'competitor-2',
            data: Array.from({ length: 7 }, (_, i) => ({
              timestamp: new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000).toISOString(),
              price: 90 + Math.random() * 20
            }))
          }
        ];
        setData(mockData);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('An error occurred'));
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [productId]);

  return { data, loading, error };
};

const startMonitoring = async (url: string) => {
  // Here you would typically make an API call to start monitoring the URL
  console.log('Starting monitoring for URL:', url);
  
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // In a real app, you would handle the API response here
  return { success: true };
};

export default function Dashboard() {
  const { t } = useTranslation();
  const [monitoredUrl, setMonitoredUrl] = useState<string | null>(null);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const { data: priceData, loading, error } = usePriceData("product-1"); // Replace with actual product ID

  // Example alert messages (replace with real-time data)
  const alerts: AlertMessage[] = [
    {
      id: "alert-1",
      productId: "product-1",
      competitorId: "competitor-1",
      message: "Price dropped by 10%",
      timestamp: new Date().toISOString(),
      language: "en",
      severity: "warning",
      isRead: false
    }
  ];

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">{t('dashboard.title')}</h1>
        <div className="flex items-center gap-2">
          {isMonitoring && (
            <div className="flex items-center text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              {t('dashboard.monitoring')} {monitoredUrl}
            </div>
          )}
          <Button variant="outline" size="sm">
            <Settings />
          </Button>
        </div>
      </div>
      
      <WebsiteMonitor 
        onMonitorStart={async (url) => {
          setIsMonitoring(true);
          setMonitoredUrl(url);
          try {
            const result = await startMonitoring(url);
            if (result.success) {
              // Handle successful monitoring start
            }
          } catch (error) {
            console.error('Failed to start monitoring:', error);
          } finally {
            setIsMonitoring(false);
          }
        }} 
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
        {/* Metrics Cards */}
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold mb-2">{t('dashboard.metrics.currentPrice')}</h3>
            <div className="text-3xl font-bold">৳1,200</div>
            <div className="text-sm text-gray-500">+2.5% today</div>
          </div>
        </Card>

        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold mb-2">{t('dashboard.metrics.priceChange')}</h3>
            <div className="text-3xl font-bold text-green-600">+3.2%</div>
            <div className="text-sm text-gray-500">Last 24 hours</div>
          </div>
        </Card>

        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold mb-2">{t('dashboard.metrics.volume')}</h3>
            <div className="text-3xl font-bold">1,250</div>
            <div className="text-sm text-gray-500">Units sold</div>
          </div>
        </Card>
      </div>

      {/* Price Trend Chart */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">{t('dashboard.charts.priceTrend')}</h3>
          <PriceTrendChart data={priceData || []} />
        </div>
      </Card>

      {/* Live Alert Feed */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">{t('dashboard.alerts.liveFeed')}</h3>
          <div className="space-y-4">
            {alerts.map((alert) => (
              <Alert
                key={alert.id}
                variant={alert.severity}
                className="p-4"
              >
                <AlertCircle className="h-4 w-4" />
                <div className="ml-2">
                  <div className="font-medium">
                    {alert.message}
                  </div>
                  <div className="text-sm text-gray-500">
                    {new Date(alert.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </Alert>
            ))}
          </div>
        </div>
      </Card>
    </div>
  );
}
