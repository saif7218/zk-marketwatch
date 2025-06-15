import { Card } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { useUserPreferences } from "@/hooks/useUserPreferences";
import { AlertMessage } from "@/types/price";

export default function Settings() {
  const { preferences, setPreferences } = useUserPreferences();

  const handleLanguageChange = (language: 'en' | 'bn') => {
    setPreferences(prev => ({
      ...prev,
      language
    }));
  };

  const handleAlertsToggle = () => {
    setPreferences(prev => ({
      ...prev,
      alertsEnabled: !prev.alertsEnabled
    }));
  };

  const handleMuteCompetitor = (competitorId: string) => {
    setPreferences(prev => ({
      ...prev,
      mutedCompetitors: prev.mutedCompetitors.includes(competitorId)
        ? prev.mutedCompetitors.filter(id => id !== competitorId)
        : [...prev.mutedCompetitors, competitorId]
    }));
  };

  const handleChartPreference = (key: keyof UserPreferences['chartPreferences']) => {
    setPreferences(prev => ({
      ...prev,
      chartPreferences: {
        ...prev.chartPreferences,
        [key]: !prev.chartPreferences[key]
      }
    }));
  };

  return (
    <div className="space-y-6">
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Language Preferences</h3>
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Switch
                checked={preferences.language === 'en'}
                onCheckedChange={() => handleLanguageChange('en')}
              />
              <Label>English</Label>
            </div>
            <div className="flex items-center space-x-2">
              <Switch
                checked={preferences.language === 'bn'}
                onCheckedChange={() => handleLanguageChange('bn')}
              />
              <Label>বাংলা</Label>
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Alert Preferences</h3>
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Switch
                checked={preferences.alertsEnabled}
                onCheckedChange={handleAlertsToggle}
              />
              <Label>Enable Real-time Alerts</Label>
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Competitor Preferences</h3>
          <div className="space-y-4">
            {/* Add competitor list here */}
            <Input placeholder="Search competitors..." />
            <div className="mt-4 space-y-2">
              {/* Example competitor */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={!preferences.mutedCompetitors.includes("competitor-1")}
                    onCheckedChange={() => handleMuteCompetitor("competitor-1")}
                  />
                  <Label>Competitor 1</Label>
                </div>
                <Button variant="ghost" size="sm">
                  Details
                </Button>
              </div>
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Chart Preferences</h3>
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Switch
                checked={preferences.chartPreferences.showTrend}
                onCheckedChange={() => handleChartPreference('showTrend')}
              />
              <Label>Show Price Trend</Label>
            </div>
            <div className="flex items-center space-x-2">
              <Switch
                checked={preferences.chartPreferences.showAnnotations}
                onCheckedChange={() => handleChartPreference('showAnnotations')}
              />
              <Label>Show Price Annotations</Label>
            </div>
            <div className="flex items-center space-x-2">
              <Switch
                checked={preferences.chartPreferences.showVolume}
                onCheckedChange={() => handleChartPreference('showVolume')}
              />
              <Label>Show Volume</Label>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
