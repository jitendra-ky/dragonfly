import { render, screen } from '@testing-library/react';

vi.mock('../components/ChatLayout', () => ({
  default: () => <div>Chat Layout</div>,
}));

import Home from './Home';

describe('Home page', () => {
  it('renders chat layout', () => {
    render(<Home />);
    expect(screen.getByText('Chat Layout')).toBeInTheDocument();
  });
});
