import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const ResetRequest = () => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post('http://localhost:3000/api/request-password-reset', { email });
      setMessage(res.data.message);
    } catch (err) {
      setMessage(err.response?.data?.message || 'Something went wrong.');
    }
  };

  return (
    <div className='auth-wrapper'>
      <form className="auth-input-container" onSubmit={handleSubmit}>
        <h2>Reset Password</h2>
        <label>Email</label>
        <input
          type="email"
          className="auth-input"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          placeholder="Enter your registered email"
        />
        <button className='auth-button-style' type="submit">Send Reset Link</button>
        <p style={{ marginTop: '20px' }}>{message}</p>
        <div style={{ marginTop: '30px' }}>
          <span className='auth-redirect' onClick={() => navigate('/auth')}>
            ← Go back to Sign In
          </span>
        </div>
      </form>
    </div>
  );
};

export default ResetRequest;
