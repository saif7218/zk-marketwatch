import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { ThemeProvider } from 'next-themes';
import { Toaster } from '@/components/ui/toaster';
import { i18n } from '@/i18n';

const queryClient = new QueryClient();

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
        <i18n.Provider>
          {children}
          <Toaster />
          <ReactQueryDevtools initialIsOpen={false} />
        </i18n.Provider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
