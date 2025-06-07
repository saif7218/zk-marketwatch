import { getLocaleFromNavigator } from 'next-intl/utils';
import { createI18n } from 'next-intl';

const i18n = createI18n({
  locales: ['en', 'bn'],
  defaultLocale: 'bn',
  fallbackLocale: {
    bn: 'en',
    default: 'en'
  },
  localeDetection: true,
  detection: {
    order: ['querystring', 'cookie', 'localStorage', 'navigator'],
    caches: ['cookie'],
    lookupQuerystring: 'lng',
    lookupCookie: 'i18next',
    lookupLocalStorage: 'i18nextLng',
    cookieMinutes: 10,
    cookieDomain: process.env.NEXT_PUBLIC_COOKIE_DOMAIN
  }
});

export const { useTranslation, initReactI18next } = i18n;

// Initialize the i18n instance
initReactI18next();

// Export the i18n instance
export default i18n;
