import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import SearchBar from '../../components/SearchBar';

describe('SearchBar Component', () => {
  const mockOnSearch = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders search input and button', () => {
    render(<SearchBar onSearch={mockOnSearch} />);
    
    expect(screen.getByPlaceholderText(/enter product name/i)).toBeInTheDocument();
    expect(screen.getByText(/compare prices/i)).toBeInTheDocument();
  });

  it('calls onSearch with input value when form is submitted', () => {
    render(<SearchBar onSearch={mockOnSearch} />);
    
    const input = screen.getByPlaceholderText(/enter product name/i);
    const button = screen.getByText(/compare prices/i);

    fireEvent.change(input, { target: { value: 'rice' } });
    fireEvent.click(button);

    expect(mockOnSearch).toHaveBeenCalledWith('rice');
  });

  it('prevents submission with empty input', () => {
    render(<SearchBar onSearch={mockOnSearch} />);
    
    const button = screen.getByText(/compare prices/i);
    fireEvent.click(button);

    expect(mockOnSearch).not.toHaveBeenCalled();
  });
}); 