'use client';

import { useState } from 'react';

interface ScrapedItem {
  item: string;
  price: number;
}

export default function PriceMonitor() {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [items, setItems] = useState<ScrapedItem[]>([]);
  const [error, setError] = useState('');
  const [isCollapsed, setIsCollapsed] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!url) {
      setError('Please enter a URL');
      return;
    }

    setIsLoading(true);
    setError('');
    setItems([]);

    try {
      const response = await fetch('http://localhost:8000/price-monitor/scrape', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch data');
      }

      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }

      setItems(data.items || []);
    } catch (err) {
      console.error('Error:', err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const totalValue = items.reduce((sum, item) => sum + (item.price || 0), 0);

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <div 
        className="flex justify-between items-center cursor-pointer mb-4"
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        <h2 className="text-2xl font-bold text-gray-800">Competitor Price Monitor</h2>
        <span className="text-gray-500">
          {isCollapsed ? '▼' : '▲'}
        </span>
      </div>
      
      {!isCollapsed && (
        <>
          <form onSubmit={handleSubmit} className="mb-6">
            <div className="flex flex-col space-y-4 md:flex-row md:space-y-0 md:space-x-4">
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Enter competitor's website URL"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
              <button
                type="submit"
                disabled={isLoading}
                className={`px-6 py-2 rounded-md text-white font-medium ${
                  isLoading
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700'
                }`}
              >
                {isLoading ? 'Scraping...' : 'Scrape Prices'}
              </button>
            </div>
          </form>

          {error && (
            <div className="mb-4 p-4 bg-red-50 border-l-4 border-red-500 text-red-700">
              <p>{error}</p>
            </div>
          )}

          {items.length > 0 && (
            <div className="overflow-x-auto">
              <div className="mb-4">
                <p className="text-sm text-gray-600">
                  Found {items.length} items • Total value: ${totalValue.toFixed(2)}
                </p>
              </div>
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Item
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Price
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {items.map((item, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {item.item}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <div className="text-sm text-gray-900 font-medium">
                          ${typeof item.price === 'number' ? item.price.toFixed(2) : 'N/A'}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
}
