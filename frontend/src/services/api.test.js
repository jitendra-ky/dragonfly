
import { API_CONFIG, STORAGE_KEYS } from '../constants';
/* eslint-env jest */
import { vi } from 'vitest';

let createdApi;
const mockAxiosPost = vi.fn();

vi.mock('axios', () => {
  const apiFn = vi.fn();
  apiFn.interceptors = {
    request: { use: vi.fn() },
    response: { use: vi.fn() },
  };
  createdApi = apiFn;

  return {
    default: {
      create: vi.fn(() => apiFn),
      post: mockAxiosPost,
    },
  };
});

describe('api service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.resetModules();
    localStorage.clear();
  });

  it('adds authorization header in request interceptor when token exists', async () => {
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, 'abc');
    await import('./api');

    const onRequest = createdApi.interceptors.request.use.mock.calls[0][0];
    const cfg = onRequest({ headers: {} });

    expect(cfg.headers.Authorization).toBe('Bearer abc');
  });

  it('refreshes token and retries original request on 401', async () => {
    await import('./api');
    localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, 'refresh-1');

    const onResponseError = createdApi.interceptors.response.use.mock.calls[0][1];
    const originalRequest = { _retry: false, headers: {} };

    mockAxiosPost.mockResolvedValueOnce({ data: { access: 'new-access' } });
    createdApi.mockResolvedValueOnce({ data: { retried: true } });

    const result = await onResponseError({
      config: originalRequest,
      response: { status: 401 },
    });

    expect(mockAxiosPost).toHaveBeenCalledWith(
      `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.TOKEN_REFRESH}`,
      { refresh: 'refresh-1' }
    );
    expect(localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)).toBe('new-access');
    expect(result).toEqual({ data: { retried: true } });
  });

  it('rejects non-401 errors without retry', async () => {
    await import('./api');
    const onResponseError = createdApi.interceptors.response.use.mock.calls[0][1];

    const error = { config: { _retry: false }, response: { status: 500 } };
    await expect(onResponseError(error)).rejects.toBe(error);
  });
});
