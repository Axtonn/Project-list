import React, { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const ResetForm = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const navigate = useNavigate();

  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState('');

  const handleReset = async (e) => {
    e.preventDefault();

    if (!newPassword || !confirmPassword) {
      setMessage('Please fill in all fields');
      return;
    }

    if (newPassword !== confirmPassword) {
      setMessage('Passwords do not match');
      return;
    }

    try {
      const res = await axios.post('http://localhost:3000/api/reset-password', {
        token,
        newPassword
      });

      setMessage(res.data.message);
      setTimeout(() => navigate('/auth'), 3000);
    } catch (err) {
      setMessage(err.response?.data?.message || 'Failed to reset password');
    }
  };

  return (
    <div className='auth-wrapper'>
      <form className="auth-input-container" onSubmit={handleReset}>
        <h2>Set New Password</h2>
        <input
          type="password"
          placeholder="New password"
          className='auth-input'
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Confirm password"
          className='auth-input'
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
        />
        <button className='auth-button-style' type="submit">Reset Password</button>
        <p style={{ marginTop: '20px' }}>{message}</p>
        <div style={{ marginTop: '30px' }}>
          <span className='auth-redirect' onClick={() => navigate('/auth')}>← Go back to Sign In</span>
        </div>
      </form>
    </div>
  );
};

export default ResetForm;