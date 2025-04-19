import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../Stylesheets/LoginForm.css';

const LoginForm = () => {
  const navigate = useNavigate();
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setCredentials({ ...credentials, [e.target.id]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:8000/authuser/login/', credentials);
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      console.log("Login success");
      navigate('/dashboard'); // Redirect after successful login
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed.');
    }
  };

  return (
    <div className="login-container">
      <div className="background-image">
        <img src="/bg_img_login.png" alt="Background" />
      </div>
      <div className="glass-card">
        {/* header */}
        <div className="card-header">
          <div className="logo">
            <img src="/logo.png" alt="SoulSetu Logo" className="logo-image" />
          </div>
          <div className="nav-links">
            <a href="#features">Features</a>
            <a href="#dashboard">Dashboard</a>
            <a href="#contact">Contact</a>
            <a href="#about">About</a>
          </div>
        </div>

        {/* main content */}
        <div className="content-container">
          <div className="left-side">
            <div className="welcome-text">
              <h1>Welcome Back</h1>
              <h2 className="blue-text">Sign In</h2>
              <p>
                Don't have an account?{' '}
                <a href="/register" className="register-link">Register Now <span className="arrow">→</span></a>
              </p>
            </div>
            <div className="side-image">
              <img src="/girl_img.png" alt="Decorative" />
            </div>
          </div>

          <div className="vertical-line"></div>

          <div className="right-side">
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <div className="input-container">
                  <input type="text" id="username" placeholder=" " onChange={handleChange} />
                  <label htmlFor="username" className="placeholder-label">Email or Username</label>
                </div>
              </div>
              <div className="form-group">
                <div className="input-container">
                  <input type="password" id="password" placeholder=" " onChange={handleChange} />
                  <label htmlFor="password" className="placeholder-label">Password</label>
                </div>
                <div className="password-options">
                  <div className="checkbox-group">
                    <input type="checkbox" id="remember" />
                    <label htmlFor="remember">Remember me</label>
                  </div>
                  <a href="#forgot" className="forgot-password">Forgot Password?</a>
                </div>
              </div>
              {error && <div className="error-message">{error}</div>}
              <button type="submit" className="submit-btn">
                <span>Get Started</span>
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;
