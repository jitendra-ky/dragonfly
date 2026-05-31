/* eslint-env jest */
import { vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Input from './Input';

describe('Input', () => {
  it('renders label, required marker, and error', () => {
    render(
      <Input
        label="Email"
        name="email"
        value=""
        onChange={() => {}}
        required
        error="Required field"
      />
    );

    expect(screen.getByText('Email')).toBeInTheDocument();
    expect(screen.getByText('*')).toBeInTheDocument();
    expect(screen.getByText('Required field')).toBeInTheDocument();
  });

  it('calls onChange on user input', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<Input name="email" value="" onChange={onChange} placeholder="you@example.com" />);

    await user.type(screen.getByPlaceholderText('you@example.com'), 'a');
    expect(onChange).toHaveBeenCalled();
  });
});
