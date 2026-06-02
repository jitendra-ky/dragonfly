import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import Button from '../components/Button';
import Input from '../components/Input';
import LoadingSpinner from '../components/LoadingSpinner';

function ForgotPassword() {
  const navigate = useNavigate();
  const forgotPassword = useAuthStore((state) => state.forgotPassword);
  const resetPassword = useAuthStore((state) => state.resetPassword);
  const [step, setStep] = useState(1); // 1: email input, 2: OTP and new password
  const [email, setEmail] = useState('');
  const [formData, setFormData] = useState({
    otp: '',
    new_password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await forgotPassword(email);
      setStep(2);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send reset code. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError('');
  };

  const handleResetSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validate passwords match
    if (formData.new_password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    // Validate password strength
    if (formData.new_password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setLoading(true);

    try {
      await resetPassword(email, formData.otp, formData.new_password);
      alert('Password reset successful! Please sign in with your new password.');
      navigate('/signin');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to reset password. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleResendOTP = async () => {
    setError('');
    setLoading(true);

    try {
      await forgotPassword(email);
      alert('Reset code has been resent to your email');
    } catch {
      setError('Failed to resend code. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Reset Password</h1>
          <p className="mt-2 text-gray-600">
            {step === 1
              ? 'Enter your email to receive a reset code'
              : 'Enter the code and your new password'}
          </p>
        </div>

        {/* Form */}
        <div className="bg-white p-8 rounded-lg shadow-md">
          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}

          {step === 1 ? (
            <form onSubmit={handleEmailSubmit}>
              <Input
                label="Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
              />

              <Button
                type="submit"
                variant="primary"
                disabled={loading}
                className="w-full flex items-center justify-center"
              >
                {loading ? <LoadingSpinner size="sm" /> : 'Send Reset Code'}
              </Button>
            </form>
          ) : (
            <form onSubmit={handleResetSubmit}>
              <div className="mb-4 p-3 bg-blue-50 border border-blue-200 text-blue-700 rounded text-sm">
                We&apos;ve sent a reset code to <strong>{email}</strong>
              </div>

              <Input
                label="Verification Code"
                type="text"
                name="otp"
                value={formData.otp}
                onChange={handleChange}
                placeholder="Enter 6-digit code"
                required
              />

              <Input
                label="New Password"
                type="password"
                name="new_password"
                value={formData.new_password}
                onChange={handleChange}
                placeholder="At least 8 characters"
                required
              />

              <Input
                label="Confirm New Password"
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="Re-enter your new password"
                required
              />

              <Button
                type="submit"
                variant="primary"
                disabled={loading}
                className="w-full flex items-center justify-center mb-2"
              >
                {loading ? <LoadingSpinner size="sm" /> : 'Reset Password'}
              </Button>

              <Button
                type="button"
                variant="secondary"
                onClick={handleResendOTP}
                disabled={loading}
                className="w-full"
              >
                Resend Code
              </Button>
            </form>
          )}

          {/* Back to Sign In Link */}
          <p className="mt-6 text-center text-sm text-gray-600">
            <Link to="/signin" className="text-primary-600 hover:text-primary-700 font-medium">
              ← Back to Sign In
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default ForgotPassword;
