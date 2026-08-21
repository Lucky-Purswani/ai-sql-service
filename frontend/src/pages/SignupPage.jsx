import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import Navbar from '../components/common/Navbar';
import { authApi } from '../api/authApi';
import { useToast } from '../context/ToastContext';
import '../styles/auth.css';

export default function SignupPage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  
  const [formData, setFormData] = useState({ email: '', password: '', password_confirm: '' });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const validate = () => {
    const newErrors = {};
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters long';
    }

    if (!formData.password_confirm) {
      newErrors.password_confirm = 'Please confirm your password';
    } else if (formData.password !== formData.password_confirm) {
      newErrors.password_confirm = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear field-specific error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    
    setIsLoading(true);
    try {
      await authApi.signup({
        email: formData.email,
        password: formData.password,
        password_confirm: formData.password_confirm
      });
      showToast('Account created successfully!', 'success');
      // Navigate to verify-otp and pass the email
      navigate('/verify-otp', { state: { email: formData.email } });
    } catch (err) {
      showToast(err.response?.data?.detail || 'An error occurred during signup', 'error');
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
            <h1 className="auth-title">Create an account</h1>
            <p className="auth-subtitle">Join us to start querying your database</p>
          </header>

          <form className="auth-form" onSubmit={handleSubmit} noValidate>
            
            <Input
              label="Email address"
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              error={errors.email}
              placeholder="you@example.com"
            />
            
            <Input
              label="Password"
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              error={errors.password}
              placeholder="Min. 8 characters"
            />

            <Input
              label="Confirm Password"
              type="password"
              name="password_confirm"
              value={formData.password_confirm}
              onChange={handleChange}
              error={errors.password_confirm}
              placeholder="Re-enter password"
            />

            <Button type="submit" fullWidth isLoading={isLoading}>
              Create Account
            </Button>
          </form>

          <footer className="auth-footer">
            Already have an account?{' '}
            <Link to="/login" className="auth-link">
              Log in
            </Link>
          </footer>
        </div>
      </main>
    </div>
  );
}
