import { render, screen } from '@testing-library/react';
import PriceComparison from '../../components/PriceComparison';

describe('PriceComparison Component', () => {
  const mockResults = {
    shwapno: { name: 'Rice 5kg', price: '৳500', store: 'Shwapno' },
    meena_bazar: { name: 'Rice 5kg', price: '৳480', store: 'Meena Bazar' },
    unimart: { name: 'Rice 5kg', price: '৳490', store: 'Unimart' }
  };

  it('renders price comparison cards correctly', () => {
    render(<PriceComparison results={mockResults} />);

    // Check if all store names are rendered
    expect(screen.getByText('Shwapno')).toBeInTheDocument();
    expect(screen.getByText('Meena Bazar')).toBeInTheDocument();
    expect(screen.getByText('Unimart')).toBeInTheDocument();

    // Check if all prices are rendered
    expect(screen.getByText('৳500')).toBeInTheDocument();
    expect(screen.getByText('৳480')).toBeInTheDocument();
    expect(screen.getByText('৳490')).toBeInTheDocument();
  });

  it('renders empty state when no results', () => {
    render(<PriceComparison results={{}} />);
    expect(screen.getByText(/no results found/i)).toBeInTheDocument();
  });

  it('renders error state when error is provided', () => {
    const error = 'Failed to fetch prices';
    render(<PriceComparison results={{}} error={error} />);
    expect(screen.getByText(error)).toBeInTheDocument();
  });
}); 