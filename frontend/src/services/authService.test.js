
/* eslint-env jest */
import { vi } from 'vitest';
import { API_CONFIG, STORAGE_KEYS } from '../constants';

const mockApi = {
  post: vi.fn(),
};

vi.mock('./api', () => ({
  default: mockApi,
}));

describe('authService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('signIn posts credentials and returns data', async () => {
    const payload = { user: { id: 1 }, access: 'a', refresh: 'r' };
    mockApi.post.mockResolvedValueOnce({ data: payload });

    const { authService } = await import('./authService');
    const result = await authService.signIn('user@example.com', 'secret');

    expect(mockApi.post).toHaveBeenCalledWith(API_CONFIG.ENDPOINTS.SIGN_IN, {
      email: 'user@example.com',
      password: 'secret',
    });
    expect(result).toEqual(payload);
  });

  it('signUp maps full_name payload key', async () => {
    mockApi.post.mockResolvedValueOnce({ data: { ok: true } });
    const { authService } = await import('./authService');

    await authService.signUp('Jane Doe', 'jane@example.com', 'password123');

    expect(mockApi.post).toHaveBeenCalledWith(API_CONFIG.ENDPOINTS.SIGN_UP, {
      full_name: 'Jane Doe',
      email: 'jane@example.com',
      password: 'password123',
    });
  });

  it('stores, reads, and clears tokens/user', async () => {
    const { authService } = await import('./authService');
    const user = { id: 99, email: 'x@y.com' };

    authService.storeTokens('access-token', 'refresh-token', user);
    expect(localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)).toBe('access-token');
    expect(localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN)).toBe('refresh-token');
    expect(authService.getStoredUser()).toEqual(user);

    authService.clearTokens();
    expect(localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)).toBeNull();
    expect(localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN)).toBeNull();
    expect(localStorage.getItem(STORAGE_KEYS.USER)).toBeNull();
    expect(authService.getStoredUser()).toBeNull();
  });
});
