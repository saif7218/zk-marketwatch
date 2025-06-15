import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useTranslation } from 'react-i18next';

interface WebsiteMonitorProps {
  onMonitorStart: (url: string) => Promise<void>;
}

export default function WebsiteMonitor({ onMonitorStart }: WebsiteMonitorProps) {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { t } = useTranslation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;
    
    try {
      setIsLoading(true);
      // Normalize URL
      const normalizedUrl = url.startsWith('http') ? url : `https://${url}`;
      await onMonitorStart(normalizedUrl);
    } catch (error) {
      console.error('Error starting monitoring:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle>{t('dashboard.monitor.title')}</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="flex flex-col space-y-4">
          <div className="flex w-full items-center space-x-2">
            <Input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder={t('dashboard.monitor.placeholder') || 'Enter grocery or competitor website URL'}
              className="flex-1"
              disabled={isLoading}
            />
            <Button 
              type="submit" 
              disabled={!url || isLoading}
              className="whitespace-nowrap"
            >
              {isLoading ? t('common.loading') : t('dashboard.monitor.start')}
            </Button>
          </div>
          <p className="text-sm text-muted-foreground">
            {t('dashboard.monitor.example')}
          </p>
        </form>
      </CardContent>
    </Card>
  );
}
