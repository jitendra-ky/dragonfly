import api from './api';
import { API_CONFIG, STORAGE_KEYS } from '../constants';

export const authService = {
  async signIn(email, password) {
    const { data } = await api.post(API_CONFIG.ENDPOINTS.SIGN_IN, { email, password });
    return data;
  },

  async signUp(fullName, email, password) {
    const { data } = await api.post(API_CONFIG.ENDPOINTS.SIGN_UP, {
      full_name: fullName,
      email,
      password,
    });
    return data;
  },

  async verifyOTP(email, otp) {
    const { data } = await api.post(API_CONFIG.ENDPOINTS.VERIFY_OTP, { email, otp });
    return data;
  },

  async googleSignIn(code) {
    const { data } = await api.post(API_CONFIG.ENDPOINTS.GOOGLE_SIGN_IN, { code });
    return data;
  },

  async forgotPassword(email) {
    const { data } = await api.post(API_CONFIG.ENDPOINTS.FORGOT_PASSWORD, { email });
    return data;
  },

  async resetPassword(email, otp, newPassword) {
    const { data } = await api.post(API_CONFIG.ENDPOINTS.RESET_PASSWORD, {
      email,
      otp,
      new_password: newPassword,
    });
    return data;
  },

  // Token management utilities
  storeTokens(access, refresh, user) {
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, access);
    localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, refresh);
    localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
  },

  clearTokens() {
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.USER);
  },

  getStoredUser() {
    const storedUser = localStorage.getItem(STORAGE_KEYS.USER);
    const accessToken = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
    
    if (storedUser && accessToken) {
      return JSON.parse(storedUser);
    }
    return null;
  },
};