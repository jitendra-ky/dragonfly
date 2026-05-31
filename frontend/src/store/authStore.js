import { create } from 'zustand';
import { authService } from '../services';

const useAuthStore = create((set) => ({
  user: null,
  loading: true,

  // Initialize auth state
  initialize: () => {
    const user = authService.getStoredUser();
    set({ user, loading: false });
  },

  // Sign in action
  signIn: async (email, password) => {
    const data = await authService.signIn(email, password);
    const { user, access, refresh } = data;

    authService.storeTokens(access, refresh, user);
    set({ user });

    return data;
  },

  // Sign up action
  signUp: async (fullName, email, password) => {
    return await authService.signUp(fullName, email, password);
  },

  // Verify OTP action
  verifyOTP: async (email, otp) => {
    const data = await authService.verifyOTP(email, otp);
    const { user, access, refresh } = data;

    authService.storeTokens(access, refresh, user);
    set({ user });

    return data;
  },

  // Google sign in action
  googleSignIn: async (code) => {
    const data = await authService.googleSignIn(code);
    const { user, access, refresh } = data;

    authService.storeTokens(access, refresh, user);
    set({ user });

    return data;
  },

  // Forgot password action
  forgotPassword: async (email) => {
    return await authService.forgotPassword(email);
  },

  // Reset password action
  resetPassword: async (email, otp, newPassword) => {
    return await authService.resetPassword(email, otp, newPassword);
  },

  // Sign out action
  signOut: () => {
    authService.clearTokens();
    set({ user: null });
  },
}));

export default useAuthStore;