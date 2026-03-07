// API Configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  ENDPOINTS: {
    // Auth endpoints
    SIGN_IN: '/api/sign-in/',
    SIGN_UP: '/api/users/',
    VERIFY_OTP: '/api/verify-otp/',
    GOOGLE_SIGN_IN: '/api/sign-in/google/',
    FORGOT_PASSWORD: '/api/forgot-password/',
    RESET_PASSWORD: '/api/reset-password/',
    TOKEN_REFRESH: '/api/token/refresh/',
    
    // Chat endpoints
    CONTACTS: '/api/contacts/',
    MESSAGES: '/api/messages/',
    ALL_USERS: '/api/all-users/',
  },
};

// LocalStorage keys
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER: 'user',
};

// App Configuration
export const APP_CONFIG = {
  NAME: 'Dragonfly',
  VERSION: '1.0.0',
};

// UI Constants
export const UI_CONFIG = {
  SIDEBAR_WIDTH: 'w-80',
  AVATAR_SIZES: {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12',
  },
};

// WebSocket Configuration
export const WEBSOCKET_CONFIG = {
  RECONNECT_INTERVAL: 3000,
  MAX_RECONNECT_ATTEMPTS: 5,
};

// Validation Constants
export const VALIDATION = {
  EMAIL_REGEX: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  MIN_PASSWORD_LENGTH: 8,
  MAX_MESSAGE_LENGTH: 1000,
};