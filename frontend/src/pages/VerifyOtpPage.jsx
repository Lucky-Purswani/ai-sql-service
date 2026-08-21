import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import Navbar from '../components/common/Navbar';
import { authApi } from '../api/authApi';
import { useToast } from '../context/ToastContext';
import '../styles/auth.css';

export default function VerifyOtpPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { showToast } = useToast();
  // We expect the email to be passed via router state from Signup
  const email = location.state?.email || '';

  const [otp, setOtp] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const validate = () => {
    if (!otp) {
      setError('OTP is required');
      return false;
    }
    if (otp.length !== 6) {
      setError('OTP must be exactly 6 characters');
      return false;
    }
    return true;
  };

  const handleChange = (e) => {
    setOtp(e.target.value);
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    
    setIsLoading(true);
    try {
      await authApi.verifyEmail({ email, otp });
      showToast('Email successfully verified!', 'success');
      setTimeout(() => {
        navigate('/login');
      }, 1500);
    } catch (err) {
      showToast(err.response?.data?.detail || 'Invalid or expired OTP', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-layout">
      <Navbar />

      <main className="auth-container">
        <div className="auth-card">
          <header className="auth-header">
            <h1 className="auth-title">Verify Email</h1>
            <p className="auth-subtitle">
              {email ? (
                <>We've sent a 6-digit code to <strong style={{color: 'white'}}>{email}</strong></>
              ) : (
                'Enter the 6-digit code sent to your email'
              )}
            </p>
          </header>

          <form className="auth-form" onSubmit={handleSubmit} noValidate>
            <Input
              label="Verification Code (OTP)"
              type="text"
              name="otp"
              value={otp}
              onChange={handleChange}
              error={error}
              placeholder="123456"
              maxLength={6}
            />

            <Button type="submit" fullWidth isLoading={isLoading}>
              Verify
            </Button>
          </form>

          <footer className="auth-footer">
            Didn't receive the code?{' '}
            <button type="button" className="auth-link" onClick={() => showToast('Resend not implemented yet', 'info')}>
              Resend
            </button>
          </footer>
        </div>
      </main>
    </div>
  );
}
