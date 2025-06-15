import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Home from '../../pages/index';
import axios from 'axios';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('Home Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the search interface', () => {
    render(<Home />);
    expect(screen.getByRole('heading', { name: /mart.*price tracker/i })).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/enter product name/i)).toBeInTheDocument();
    const buttons = screen.getAllByText(/compare prices/i);
    expect(buttons[0].tagName).toBe('BUTTON');
  });

  it('handles successful search', async () => {
    const mockResults = {
      shwapno: { name: 'Rice 5kg', price: '৳500', store: 'Shwapno' },
      meena_bazar: { name: 'Rice 5kg', price: '৳480', store: 'Meena Bazar' },
      unimart: { name: 'Rice 5kg', price: '৳490', store: 'Unimart' }
    };

    mockedAxios.get.mockResolvedValueOnce({ data: { results: mockResults } });

    render(<Home />);
    
    const input = screen.getByPlaceholderText(/enter product name/i);
    const button = screen.getAllByText(/compare prices/i).find(el => el.tagName === 'BUTTON')!;

    fireEvent.change(input, { target: { value: 'rice' } });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Shwapno')).toBeInTheDocument();
      expect(screen.getByText('৳500')).toBeInTheDocument();
    });
  });

  it('handles search error', async () => {
    mockedAxios.get.mockRejectedValueOnce(new Error('Network error'));

    render(<Home />);
    
    const input = screen.getByPlaceholderText(/enter product name/i);
    const button = screen.getAllByText(/compare prices/i).find(el => el.tagName === 'BUTTON')!;

    fireEvent.change(input, { target: { value: 'rice' } });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/failed to fetch price comparison/i)).toBeInTheDocument();
    });
  });

  it('shows loading state during search', async () => {
    mockedAxios.get.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    render(<Home />);
    
    const input = screen.getByPlaceholderText(/enter product name/i);
    const button = screen.getAllByText(/compare prices/i).find(el => el.tagName === 'BUTTON')!;

    fireEvent.change(input, { target: { value: 'rice' } });
    fireEvent.click(button);

    expect(screen.getByLabelText('Loading')).toBeInTheDocument();
  });
}); 