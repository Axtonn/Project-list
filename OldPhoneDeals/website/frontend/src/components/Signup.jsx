import { useNavigate } from 'react-router-dom';
import React, { useState } from 'react';
import axios from 'axios';
import './Auth.css';

function Signup({ onToggle }) {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    inputFirstName: '',
    inputLastName: '',
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
      await axios.post('http://localhost:3000/api/sign-up', form);

      alert('Signup successful! Please check your email for verification');
      onToggle();
      navigate('/auth');
    } catch (err) {
      if (err.response && err.response.data) {
        alert(`${err.response.data.error}:\n${err.response.data.details || ''}`);
      } else {
        alert('An error occurred. Please try again.');
      }
      console.error('Signup error:', err);
    }
    setForm({
      inputFirstName: '',
      inputLastName: '',
      inputEmail: '',
      inputPassword: ''
    })
  };

  return (
    <div className='auth-wrapper'>
      <form className="auth-input-container" onSubmit={handleSubmit}>
        <h2>User Sign-Up</h2>
        <div className="container">
          <label htmlFor="firstName">First Name</label>
          <input className='auth-input' type="text" id="firstName" name="inputFirstName"
            placeholder="Enter First Name" autoComplete="off" required
            value={form.inputFirstName} onChange={handleChange} />
        </div>

        <div>
          <label htmlFor="lastName">Last Name</label>
          <input className='auth-input' type="text" id="lastName" name="inputLastName"
            placeholder="Enter Last Name" autoComplete="off" required
            value={form.inputLastName} onChange={handleChange} />
        </div>

        <div>
          <label htmlFor="email">Email</label>
          <input className='auth-input' type="email" id="email" name="inputEmail"
            placeholder="Enter Email" autoComplete="off" required
            value={form.inputEmail} onChange={handleChange} />
        </div>

        <div>
          <label htmlFor="password">Password</label>
          <input className='auth-input' type="password" id="password" name="inputPassword"
            placeholder="Enter Password" autoComplete="off" required
            value={form.inputPassword} onChange={handleChange} />
        </div>

        <button type="submit" className='auth-button-style'>Submit</button>

        <div style={{ marginTop: '30px' }}>
          Already have an account? <span className='auth-redirect' onClick={onToggle}>Sign in</span>
        </div>
        <div>
          Go back to Home? <span className='auth-redirect' onClick={() => navigate('/')}>Home</span>
        </div>
      </form>
    </div>
  );
}

export default Signup;
