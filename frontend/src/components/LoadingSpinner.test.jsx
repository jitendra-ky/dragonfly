/* eslint-env jest */
import { render } from '@testing-library/react';
import LoadingSpinner from './LoadingSpinner';

describe('LoadingSpinner', () => {
  it('renders with default classes', () => {
    const { container } = render(<LoadingSpinner />);
    expect(container.firstChild.className).toContain('animate-spin');
  });

  it('renders with large size class', () => {
    const { container } = render(<LoadingSpinner size="lg" className="extra" />);
    expect(container.firstChild.className).toContain('w-12');
    expect(container.firstChild.className).toContain('extra');
  });
});
