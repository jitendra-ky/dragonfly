import { API_CONFIG, STORAGE_KEYS, APP_CONFIG, UI_CONFIG, WEBSOCKET_CONFIG, VALIDATION } from './index';

describe('constants', () => {
  it('exposes API endpoints and base URL', () => {
    expect(API_CONFIG.BASE_URL).toBeTruthy();
    expect(API_CONFIG.ENDPOINTS.SIGN_IN).toBe('/api/sign-in/');
    expect(API_CONFIG.ENDPOINTS.MESSAGES).toBe('/api/messages/');
  });

  it('exposes storage keys and app config', () => {
    expect(STORAGE_KEYS.ACCESS_TOKEN).toBe('access_token');
    expect(APP_CONFIG.NAME).toBe('Dragonfly');
    expect(APP_CONFIG.VERSION).toBe('1.0.0');
  });

  it('exposes UI, websocket and validation constants', () => {
    expect(UI_CONFIG.AVATAR_SIZES.md).toContain('w-10');
    expect(WEBSOCKET_CONFIG.MAX_RECONNECT_ATTEMPTS).toBe(5);
    expect(VALIDATION.MIN_PASSWORD_LENGTH).toBe(8);
    expect(VALIDATION.EMAIL_REGEX.test('user@example.com')).toBe(true);
  });
});