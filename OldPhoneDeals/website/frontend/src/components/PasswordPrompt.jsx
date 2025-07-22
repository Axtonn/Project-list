import React from 'react';

const PasswordPrompt = ({ onConfirm, onCancel, setPassword }) => (
  <div>
    <input type="password" placeholder="Enter password" onChange={e => setPassword(e.target.value)} />
    <button onClick={onConfirm}>Done</button>
    <button onClick={onCancel}>Cancel</button>
  </div>
);

export default PasswordPrompt;
