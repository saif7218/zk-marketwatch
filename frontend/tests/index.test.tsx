import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Home from '../pages/index';
import axios from 'axios';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('Home Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the search input', () => {
    render(<Home />);
    expect(screen.getByPlaceholderText(/enter product name/i)).toBeInTheDocument();
  });

  it('handles search submission', async () => {
    const mockResponse = {
      data: {
        product: 'rice',
        results: {
          shwapno: { name: 'Rice 5kg', price: '৳500', store: 'Shwapno' },
          meena_bazar: { name: 'Rice 5kg', price: '৳480', store: 'Meena Bazar' },
          unimart: { name: 'Rice 5kg', price: '৳490', store: 'Unimart' }
        }
      }
    };

    mockedAxios.get.mockResolvedValueOnce(mockResponse);

    render(<Home />);
    
    const input = screen.getByPlaceholderText(/enter product name/i);
    const button = screen.getByText(/compare prices/i);

    fireEvent.change(input, { target: { value: 'rice' } });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/rice 5kg/i)).toBeInTheDocument();
      expect(screen.getByText(/৳500/i)).toBeInTheDocument();
    });
  });

  it('handles search error', async () => {
    mockedAxios.get.mockRejectedValueOnce(new Error('Network error'));

    render(<Home />);
    
    const input = screen.getByPlaceholderText(/enter product name/i);
    const button = screen.getByText(/compare prices/i);

    fireEvent.change(input, { target: { value: 'rice' } });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/failed to fetch price comparison/i)).toBeInTheDocument();
    });
  });
}); 