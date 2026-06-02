
/* eslint-env jest */
import { vi } from 'vitest';

import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

let authState = { user: null, loading: false };

vi.mock('./store/authStore', () => ({
  default: (selector) => selector(authState),
}));

vi.mock('./pages/SignIn', () => ({ default: () => <div>Sign In Page</div> }));
vi.mock('./pages/SignUp', () => ({ default: () => <div>Sign Up Page</div> }));
vi.mock('./pages/ForgotPassword', () => ({ default: () => <div>Forgot Page</div> }));
vi.mock('./pages/Home', () => ({ default: () => <div>Home Page</div> }));

import AppRoutes from './routes';

describe('AppRoutes', () => {
  it('shows loading state while auth is loading', () => {
    authState = { user: null, loading: true };
    render(
      <MemoryRouter initialEntries={['/']}>
        <AppRoutes />
      </MemoryRouter>
    );

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('redirects unauthenticated root route to sign in', () => {
    authState = { user: null, loading: false };
    render(
      <MemoryRouter initialEntries={['/']}>
        <AppRoutes />
      </MemoryRouter>
    );

    expect(screen.getByText('Sign In Page')).toBeInTheDocument();
  });

  it('renders protected home when authenticated', () => {
    authState = { user: { id: 1 }, loading: false };
    render(
      <MemoryRouter initialEntries={['/']}>
        <AppRoutes />
      </MemoryRouter>
    );

    expect(screen.getByText('Home Page')).toBeInTheDocument();
  });

  it('renders public auth pages', () => {
    authState = { user: null, loading: false };
    render(
      <MemoryRouter initialEntries={['/signup']}>
        <AppRoutes />
      </MemoryRouter>
    );
    expect(screen.getByText('Sign Up Page')).toBeInTheDocument();

    render(
      <MemoryRouter initialEntries={['/forgot-password']}>
        <AppRoutes />
      </MemoryRouter>
    );
    expect(screen.getByText('Forgot Page')).toBeInTheDocument();
  });
});

