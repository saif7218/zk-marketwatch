import { useState, useEffect } from 'react';
import { UserPreferences } from '../types/price';

const DEFAULT_PREFERENCES: UserPreferences = {
  mutedCompetitors: [],
  language: 'bn',
  alertsEnabled: true,
  chartPreferences: {
    showTrend: true,
    showAnnotations: true,
    showVolume: true
  }
};

export const useUserPreferences = () => {
  const [preferences, setPreferences] = useState<UserPreferences>(DEFAULT_PREFERENCES);

  // Load from localStorage
  useEffect(() => {
    const savedPrefs = localStorage.getItem('apon-mart-prefs');
    if (savedPrefs) {
      try {
        const parsedPrefs = JSON.parse(savedPrefs);
        setPreferences(prev => ({
          ...prev,
          ...parsedPrefs
        }));
      } catch (error) {
        console.error('Failed to load preferences:', error);
      }
    }
  }, []);

  // Sync with localStorage
  useEffect(() => {
    localStorage.setItem('apon-mart-prefs', JSON.stringify(preferences));
  }, [preferences]);

  // Sync with Supabase (optional)
  const syncWithSupabase = async () => {
    try {
      // TODO: Implement Supabase sync
      console.log('Syncing preferences with Supabase:', preferences);
    } catch (error) {
      console.error('Failed to sync with Supabase:', error);
    }
  };

  return {
    preferences,
    setPreferences,
    syncWithSupabase
  };
};
