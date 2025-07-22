import React from 'react';

const EmailNotification = ({ email }) => (
  <div>
    <h3>Password Changed!</h3>
    <p>An email has been sent to {email} for more details.</p>
  </div>
);

export default EmailNotification;
