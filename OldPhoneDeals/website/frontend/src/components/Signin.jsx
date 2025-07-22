import { useNavigate } from 'react-router-dom';
import React, { useState } from 'react';
import axios from 'axios';
import './Auth.css';

function Signin({ onToggle, isAdmin }) {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    inputEmail: '',
    inputPassword: ''
  });

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (isAdmin) {
        await axios.post('http://localhost:3000/api/admin-sign-in', form, {
          withCredentials: true
        });
        alert('Admin Login successful!');
        navigate('/admin-view');
      } else {
        await axios.post('http://localhost:3000/api/sign-in', form, {
          withCredentials: true
        });
        alert('Login successful!');
        navigate('/'); // or wherever you want to go
      }
    } catch (err) {
      if (err.response && err.response.data) {
        alert(err.response.data.message || 'Signin failed');
      } else {
        alert('An error occurred. Please try again.');
      }
      setForm({inputEmail: '', inputPassword: ''})
      console.error('Signin error:', err);
    }
  };
  
  return (
    <div className='auth-wrapper'>
      <form className="auth-input-container" onSubmit={handleSubmit}>
        {isAdmin ? <h2>Admin Sign-In</h2> : <h2>User Sign-In</h2>}
        <div>
          <label htmlFor="email">Email</label>
          <input className='auth-input' type="email" id="email" name="inputEmail"
            placeholder="Enter Email here" required autoComplete="off"
            value={form.inputEmail}
            onChange={handleChange} />
        </div>

        <div>
          <label htmlFor="password">Password</label>
          <input className='auth-input' type="password" id="password" name="inputPassword"
            placeholder="Enter Password here" autoComplete="off" required
            value={form.inputPassword}
            onChange={handleChange} />
        </div>
        <button type="submit" className='auth-button-style'>Submit</button>
        <div>
          <span className='auth-redirect' onClick={() => navigate('/reset-password')}>
            Forgot Password?
          </span>
        </div>

        {!isAdmin && (
          <div style={{ marginTop: '30px' }}>
            Don't have an account? <span className='auth-redirect' onClick={onToggle}>Sign up</span>
          </div>
        )}
        <div>
          Go back to Home? <span className='auth-redirect' onClick={() => navigate('/')}>Home</span>
        </div>
      </form>
    </div>
  );
}

export default Signin;
