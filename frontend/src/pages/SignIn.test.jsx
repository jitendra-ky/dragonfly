
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import SignIn from './SignIn';

/* eslint-env jest */
import { vi } from 'vitest';

const mockNavigate = vi.fn();
const mockSignIn = vi.fn();
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
  signIn: mockSignIn,
  googleSignIn: mockGoogleSignIn,
};

vi.mock('../store/authStore', () => ({
  default: (selector) => selector(authState),
}));

describe('SignIn page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.stubEnv('VITE_DEV_MODE', 'false');
    authState = { user: null, signIn: mockSignIn, googleSignIn: mockGoogleSignIn };
  });

  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it('submits credentials and navigates home on success', async () => {
    const user = userEvent.setup();
    mockSignIn.mockResolvedValueOnce({ ok: true });

    render(
      <MemoryRouter>
        <SignIn />
      </MemoryRouter>
    );

    await user.type(screen.getByPlaceholderText('you@example.com'), 'me@example.com');
    await user.type(screen.getByPlaceholderText('Enter your password'), 'password123');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(mockSignIn).toHaveBeenCalledWith('me@example.com', 'password123');
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });
  });

  it('shows invalid credentials message on sign-in error', async () => {
    const user = userEvent.setup();
    mockSignIn.mockRejectedValueOnce(new Error('bad creds'));

    render(
      <MemoryRouter>
        <SignIn />
      </MemoryRouter>
    );

    await user.type(screen.getByPlaceholderText('you@example.com'), 'me@example.com');
    await user.type(screen.getByPlaceholderText('Enter your password'), 'password123');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(screen.getByText('Invalid email or password')).toBeInTheDocument();
    });
  });

  it('shows all seeded test users in dev mode', () => {
    vi.stubEnv('VITE_DEV_MODE', 'true');

    render(
      <MemoryRouter>
        <SignIn />
      </MemoryRouter>
    );

    expect(screen.getByText('Test users')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Login as Alice' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Login as Bob' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Login as Carol' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Login as Dave' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Login as Eve' })).toBeInTheDocument();
  });

  it('hides seeded test users outside dev mode', () => {
    render(
      <MemoryRouter>
        <SignIn />
      </MemoryRouter>
    );

    expect(screen.queryByText('Test users')).not.toBeInTheDocument();
  });

  it('logs in with a selected seeded test user', async () => {
    const user = userEvent.setup();
    vi.stubEnv('VITE_DEV_MODE', 'true');
    mockSignIn.mockResolvedValueOnce({ ok: true });

    render(
      <MemoryRouter>
        <SignIn />
      </MemoryRouter>
    );

    await user.click(screen.getByRole('button', { name: 'Login as Carol' }));

    await waitFor(() => {
      expect(mockSignIn).toHaveBeenCalledWith('carol@example.com', 'password123');
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });
  });
});
