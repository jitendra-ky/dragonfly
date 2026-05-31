import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import ForgotPassword from './ForgotPassword';

const mockNavigate = vi.fn();
const mockForgotPassword = vi.fn();
const mockResetPassword = vi.fn();

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

vi.mock('../store/authStore', () => ({
  default: (selector) =>
    selector({
      forgotPassword: mockForgotPassword,
      resetPassword: mockResetPassword,
    }),
}));

describe('ForgotPassword page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(window, 'alert').mockImplementation(() => {});
  });

  it('moves to step 2 after sending reset code', async () => {
    const user = userEvent.setup();
    mockForgotPassword.mockResolvedValueOnce({ ok: true });

    render(
      <MemoryRouter>
        <ForgotPassword />
      </MemoryRouter>
    );

    await user.type(screen.getByPlaceholderText('you@example.com'), 'me@example.com');
    await user.click(screen.getByRole('button', { name: /send reset code/i }));

    await waitFor(() => {
      expect(screen.getByText(/we've sent a reset code/i)).toBeInTheDocument();
    });
  });

  it('validates matching password on reset step', async () => {
    const user = userEvent.setup();
    mockForgotPassword.mockResolvedValueOnce({ ok: true });

    render(
      <MemoryRouter>
        <ForgotPassword />
      </MemoryRouter>
    );

    await user.type(screen.getByPlaceholderText('you@example.com'), 'me@example.com');
    await user.click(screen.getByRole('button', { name: /send reset code/i }));

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Enter 6-digit code')).toBeInTheDocument();
    });

    await user.type(screen.getByPlaceholderText('Enter 6-digit code'), '111111');
    await user.type(screen.getByPlaceholderText('At least 8 characters'), 'password123');
    await user.type(screen.getByPlaceholderText('Re-enter your new password'), 'different');
    await user.click(screen.getByRole('button', { name: /reset password/i }));

    expect(screen.getByText('Passwords do not match')).toBeInTheDocument();
  });

  it('resets password and navigates to signin', async () => {
    const user = userEvent.setup();
    mockForgotPassword.mockResolvedValueOnce({ ok: true });
    mockResetPassword.mockResolvedValueOnce({ ok: true });

    render(
      <MemoryRouter>
        <ForgotPassword />
      </MemoryRouter>
    );

    await user.type(screen.getByPlaceholderText('you@example.com'), 'me@example.com');
    await user.click(screen.getByRole('button', { name: /send reset code/i }));

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Enter 6-digit code')).toBeInTheDocument();
    });

    await user.type(screen.getByPlaceholderText('Enter 6-digit code'), '111111');
    await user.type(screen.getByPlaceholderText('At least 8 characters'), 'password123');
    await user.type(screen.getByPlaceholderText('Re-enter your new password'), 'password123');
    await user.click(screen.getByRole('button', { name: /reset password/i }));

    await waitFor(() => {
      expect(mockResetPassword).toHaveBeenCalledWith('me@example.com', '111111', 'password123');
      expect(mockNavigate).toHaveBeenCalledWith('/signin');
    });
  });
});
