const nodemailer = require('nodemailer');
require('dotenv').config();

const transporter = nodemailer.createTransport({
  service: 'Gmail',
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS,
  },
});

const sendEmail = async (to, subject, html) => {
  await transporter.sendMail({
    from: process.env.EMAIL_USER,
    to,
    subject,
    html
  });
};

// 🔒 Email notification for password change
const sendPasswordChangeEmail = async (to, name) => {
  const html = `
    <p>Hi ${name},</p>
    <p>Your password has been changed successfully.</p>
    <p>If this wasn't you, please reset your password immediately or contact support.</p>
  `;
  await sendEmail(to, 'Your Password Was Changed', html);
};

// 👤 Email notification for profile update
const sendProfileUpdateEmail = async (to, name) => {
  const html = `
    <p>Hi ${name},</p>
    <p>Your profile information was recently updated.</p>
    <p>If this wasn't you, please review your account activity or contact support.</p>
  `;
  await sendEmail(to, 'Your Profile Was Updated', html);
};

module.exports = {
  sendEmail,
  sendPasswordChangeEmail,
  sendProfileUpdateEmail
};
