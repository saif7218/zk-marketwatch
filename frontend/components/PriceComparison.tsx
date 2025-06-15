import React from 'react';

interface PriceResult {
  name: string;
  price: string;
  store: string;
}

interface PriceComparisonProps {
  results: Record<string, PriceResult>;
  error?: string;
}

const PriceComparison: React.FC<PriceComparisonProps> = ({ results, error }) => {
  if (error) {
    return (
      <div className="text-red-500 text-center p-4">
        {error}
      </div>
    );
  }

  if (Object.keys(results).length === 0) {
    return (
      <div className="text-gray-500 text-center p-4">
        No results found
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4">
      {Object.entries(results).map(([store, result]) => (
        <div
          key={store}
          className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow"
        >
          <h3 className="text-lg font-semibold text-gray-800">{result.store}</h3>
          <p className="text-gray-600 mt-2">{result.name}</p>
          <p className="text-2xl font-bold text-green-600 mt-2">{result.price}</p>
        </div>
      ))}
    </div>
  );
};

export default PriceComparison; 