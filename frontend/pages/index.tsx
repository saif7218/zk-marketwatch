import { useState } from 'react';
import axios from 'axios';
import { MagnifyingGlassIcon, ArrowPathIcon } from '@heroicons/react/24/outline';

interface PriceResult {
  name?: string;
  price?: string;
  error?: string;
  store: string;
}

interface ComparisonResult {
  product: string;
  results: {
    shwapno: PriceResult;
    meena_bazar: PriceResult;
    unimart: PriceResult;
  };
}

export default function Home() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<ComparisonResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await axios.get(`${process.env.NEXT_PUBLIC_BACKEND_URL}/compare`, {
        params: { product: query }
      });
      setResults(response.data);
    } catch (err) {
      setError('Failed to fetch price comparison. Please try again.');
      console.error('Error fetching prices:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <h1 className="text-2xl font-bold text-gray-900 flex items-center justify-center">
            <span className="text-blue-600">Mart</span> Price Tracker
          </h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        {/* Search Section */}
        <div className="max-w-3xl mx-auto">
          <div className="flex flex-col space-y-4">
            <div className="relative group">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Enter product name (e.g., rice, oil, milk)"
                className="w-full px-4 py-3 pl-12 text-gray-900 border border-gray-300 rounded-lg 
                         focus:ring-2 focus:ring-blue-500 focus:border-blue-500 
                         transition-all duration-200 ease-in-out
                         group-hover:border-blue-400"
              />
              <MagnifyingGlassIcon className="absolute left-4 top-3.5 h-6 w-6 text-gray-400 
                                           group-hover:text-blue-500 transition-colors duration-200" />
            </div>
            <button
              onClick={handleSearch}
              disabled={loading}
              className="w-full px-4 py-3 text-white bg-blue-600 rounded-lg 
                       hover:bg-blue-700 focus:outline-none focus:ring-2 
                       focus:ring-blue-500 focus:ring-offset-2 
                       disabled:opacity-50 disabled:cursor-not-allowed
                       transition-all duration-200 ease-in-out
                       transform hover:scale-[1.02] active:scale-[0.98]"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <ArrowPathIcon className="w-5 h-5 mr-2 animate-spin" />
                  Searching...
                </span>
              ) : (
                'Compare Prices'
              )}
            </button>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg animate-fade-in">
              <p className="text-red-600">{error}</p>
            </div>
          )}

          {/* Results Section */}
          {results && (
            <div className="mt-8 space-y-6 animate-fade-in">
              <h2 className="text-xl font-semibold text-gray-900 text-center">
                Price Comparison for "{results.product}"
              </h2>
              
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {Object.entries(results.results).map(([store, data]) => (
                  <div
                    key={store}
                    className="bg-white p-6 rounded-lg shadow-sm border border-gray-200
                             hover:shadow-md transition-shadow duration-200
                             transform hover:scale-[1.02]"
                  >
                    <h3 className="text-lg font-medium text-gray-900 capitalize">
                      {store.replace('_', ' ')}
                    </h3>
                    {data.error ? (
                      <p className="mt-2 text-red-600">{data.error}</p>
                    ) : (
                      <>
                        <p className="mt-2 text-gray-600 line-clamp-2">{data.name}</p>
                        <p className="mt-2 text-2xl font-bold text-blue-600">
                          {data.price}
                        </p>
                      </>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-8">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <p className="text-center text-gray-500 text-sm">
            Compare prices across Shwapno, Meena Bazar, and Unimart
          </p>
        </div>
      </footer>
    </div>
  );
} 