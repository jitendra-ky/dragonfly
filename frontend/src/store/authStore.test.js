
/* eslint-env jest */
import { vi } from 'vitest';

const mockAuthService = {
  getStoredUser: vi.fn(),
  signIn: vi.fn(),
  signUp: vi.fn(),
  verifyOTP: vi.fn(),
  googleSignIn: vi.fn(),
  forgotPassword: vi.fn(),
  resetPassword: vi.fn(),
  storeTokens: vi.fn(),
  clearTokens: vi.fn(),
};

vi.mock('../services', () => ({
  authService: mockAuthService,
}));

describe('authStore', () => {
  beforeEach(async () => {
    vi.clearAllMocks();
    const { default: useAuthStore } = await import('./authStore');
    useAuthStore.setState({ user: null, loading: true });
  });

  it('initializes from storage', async () => {
    const user = { id: 1, email: 'user@example.com' };
    mockAuthService.getStoredUser.mockReturnValueOnce(user);

    const { default: useAuthStore } = await import('./authStore');
    useAuthStore.getState().initialize();

    expect(useAuthStore.getState().user).toEqual(user);
    expect(useAuthStore.getState().loading).toBe(false);
  });

  it('signIn stores tokens and updates user', async () => {
    const data = { user: { id: 2 }, access: 'a', refresh: 'r' };
    mockAuthService.signIn.mockResolvedValueOnce(data);

    const { default: useAuthStore } = await import('./authStore');
    const result = await useAuthStore.getState().signIn('a@b.com', 'pw');

    expect(mockAuthService.storeTokens).toHaveBeenCalledWith('a', 'r', { id: 2 });
    expect(useAuthStore.getState().user).toEqual({ id: 2 });
    expect(result).toEqual(data);
  });

  it('verifyOTP and googleSignIn also store tokens', async () => {
    const otpData = { user: { id: 3 }, access: 'a1', refresh: 'r1' };
    const googleData = { user: { id: 4 }, access: 'a2', refresh: 'r2' };
    mockAuthService.verifyOTP.mockResolvedValueOnce(otpData);
    mockAuthService.googleSignIn.mockResolvedValueOnce(googleData);

    const { default: useAuthStore } = await import('./authStore');

    await useAuthStore.getState().verifyOTP('x@y.com', '123456');
    expect(mockAuthService.storeTokens).toHaveBeenCalledWith('a1', 'r1', { id: 3 });

    await useAuthStore.getState().googleSignIn('code');
    expect(mockAuthService.storeTokens).toHaveBeenCalledWith('a2', 'r2', { id: 4 });
  });

  it('forwards signUp/forgotPassword/resetPassword and signOut clears user', async () => {
    mockAuthService.signUp.mockResolvedValueOnce({ created: true });
    mockAuthService.forgotPassword.mockResolvedValueOnce({ sent: true });
    mockAuthService.resetPassword.mockResolvedValueOnce({ reset: true });

    const { default: useAuthStore } = await import('./authStore');

    await expect(useAuthStore.getState().signUp('Jane', 'j@x.com', 'password')).resolves.toEqual({ created: true });
    await expect(useAuthStore.getState().forgotPassword('j@x.com')).resolves.toEqual({ sent: true });
    await expect(useAuthStore.getState().resetPassword('j@x.com', '111111', 'newpassword')).resolves.toEqual({ reset: true });

    useAuthStore.setState({ user: { id: 9 } });
    useAuthStore.getState().signOut();
    expect(mockAuthService.clearTokens).toHaveBeenCalled();
    expect(useAuthStore.getState().user).toBeNull();
  });
});
