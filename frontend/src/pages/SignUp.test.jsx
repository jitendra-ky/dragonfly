import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import SignUp from './SignUp';

const mockNavigate = vi.fn();
const mockSignUp = vi.fn();
const mockVerifyOTP = vi.fn();
const mockGoogleSignIn = vi.fn();

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

let authState = {
  user: null,
  signUp: mockSignUp,
  verifyOTP: mockVerifyOTP,
  googleSignIn: mockGoogleSignIn,
};

vi.mock('../store/authStore', () => ({
  default: (selector) => selector(authState),
}));

describe('SignUp page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    authState = {
      user: null,
      signUp: mockSignUp,
      verifyOTP: mockVerifyOTP,
      googleSignIn: mockGoogleSignIn,
    };
  });

  it('validates password mismatch', async () => {
    render(
      <MemoryRouter>
        <SignUp />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByPlaceholderText('John Doe'), { target: { value: 'Jane Doe' } });
    fireEvent.change(screen.getByPlaceholderText('you@example.com'), { target: { value: 'jane@example.com' } });
    fireEvent.change(screen.getByPlaceholderText('At least 8 characters'), { target: { value: 'password123' } });
    fireEvent.change(screen.getByPlaceholderText('Re-enter your password'), { target: { value: 'mismatch123' } });
    fireEvent.click(screen.getByRole('button', { name: /sign up/i }));

    expect(screen.getByText('Passwords do not match')).toBeInTheDocument();
  });

  it('submits signup and opens OTP modal', async () => {
    mockSignUp.mockResolvedValueOnce({ ok: true });

    render(
      <MemoryRouter>
        <SignUp />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByPlaceholderText('John Doe'), { target: { value: 'Jane Doe' } });
    fireEvent.change(screen.getByPlaceholderText('you@example.com'), { target: { value: 'jane@example.com' } });
    fireEvent.change(screen.getByPlaceholderText('At least 8 characters'), { target: { value: 'password123' } });
    fireEvent.change(screen.getByPlaceholderText('Re-enter your password'), { target: { value: 'password123' } });
    fireEvent.click(screen.getByRole('button', { name: /sign up/i }));

    await waitFor(() => {
      expect(mockSignUp).toHaveBeenCalledWith('Jane Doe', 'jane@example.com', 'password123');
      expect(screen.getByText('Verify Your Email')).toBeInTheDocument();
    });
  });
});
