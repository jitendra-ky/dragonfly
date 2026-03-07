import { create } from 'zustand';
import { authService } from '../services';

const useAuthStore = create((set, get) => ({
  user: null,
  loading: true,

  // Initialize auth state
  initialize: () => {
    const user = authService.getStoredUser();
    set({ user, loading: false });
  },

  // Sign in action
  signIn: async (email, password) => {
    try {
      const data = await authService.signIn(email, password);
      const { user, access, refresh } = data;
      
      authService.storeTokens(access, refresh, user);
      set({ user });
      
      return data;
    } catch (error) {
      throw error;
    }
  },

  // Sign up action
  signUp: async (fullName, email, password) => {
    try {
      const data = await authService.signUp(fullName, email, password);
      return data;
    } catch (error) {
      throw error;
    }
  },

  // Verify OTP action
  verifyOTP: async (email, otp) => {
    try {
      const data = await authService.verifyOTP(email, otp);
      const { user, access, refresh } = data;
      
      authService.storeTokens(access, refresh, user);
      set({ user });
      
      return data;
    } catch (error) {
      throw error;
    }
  },

  // Google sign in action
  googleSignIn: async (code) => {
    try {
      const data = await authService.googleSignIn(code);
      const { user, access, refresh } = data;
      
      authService.storeTokens(access, refresh, user);
      set({ user });
      
      return data;
    } catch (error) {
      throw error;
    }
  },

  // Forgot password action
  forgotPassword: async (email) => {
    try {
      const data = await authService.forgotPassword(email);
      return data;
    } catch (error) {
      throw error;
    }
  },

  // Reset password action
  resetPassword: async (email, otp, newPassword) => {
    try {
      const data = await authService.resetPassword(email, otp, newPassword);
      return data;
    } catch (error) {
      throw error;
    }
  },

  // Sign out action
  signOut: () => {
    authService.clearTokens();
    set({ user: null });
  },
}));

export default useAuthStore;