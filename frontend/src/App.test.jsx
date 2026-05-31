import { render, screen } from '@testing-library/react';

const mockInitialize = vi.fn();

vi.mock('./store/authStore', () => ({
  default: (selector) => selector({ initialize: mockInitialize }),
}));

vi.mock('./routes', () => ({
  default: () => <div>Mocked Routes</div>,
}));

import App from './App';

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('initializes auth and renders routes', () => {
    render(<App />);
    expect(mockInitialize).toHaveBeenCalled();
    expect(screen.getByText('Mocked Routes')).toBeInTheDocument();
  });
});
