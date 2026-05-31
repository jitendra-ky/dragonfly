import { render, screen } from '@testing-library/react';
import Avatar from './Avatar';

describe('Avatar', () => {
  it('renders initials and custom size', () => {
    render(<Avatar name="Jane Doe" size="lg" />);
    expect(screen.getByText('JD')).toBeInTheDocument();
  });

  it('renders fallback when no name is provided', () => {
    render(<Avatar />);
    expect(screen.getByText('?')).toBeInTheDocument();
  });
});
