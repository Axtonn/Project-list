const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const User = require('../models/User'); 
const logAdminAction = require('../helper/logAdmin');
const { validatePassword } = require('../helper/validatePassword');
const { sendEmail } = require('../helper/sendEmail');
require('dotenv').config();

// User Sign-In
exports.signIn = async (req, res) => {
  const { inputEmail, inputPassword } = req.body;

  try {
    const loginUser = await User.findOne({ email: inputEmail });
    if (!loginUser) {
      return res.status(404).json({ message: `No user found with email: ${inputEmail}` });
    }

    // Resend verification email if user is not verified
    if (!loginUser.isverified) {
      const verificationToken = jwt.sign(
        { userId: loginUser._id, email: loginUser.email },
        process.env.JWT_SECRET,
        { expiresIn: '10m' }
      );
      const verificationLink = `http://localhost:5173/verify-email?token=${verificationToken}`;

      const emailBody = `
        <p>Hello ${loginUser.firstname},</p>
        <p>Old Phone Deals would like you to please verify your email by clicking the link below:</p>
        <a href="${verificationLink}">Verify Email</a>
        <br>
        <p>If you did not request this, please ignore this email.</p>
      `;

      await sendEmail(loginUser.email, 'Verify your email', emailBody);

      return res.status(401).json({
        message: 'Please verify your email before signing-in! A new verification link has been sent.'
      });
    }

    if (loginUser.role === 'admin') {
      return res.status(403).json({ message: 'Admins must login through the admin portal' });
    }

    const passwordMatch = await bcrypt.compare(inputPassword, loginUser.password);
    if (!passwordMatch) {
      return res.status(401).json({ message: 'Password is incorrect' });
    }

    const token = jwt.sign(
      { firstname: loginUser.firstname, lastname: loginUser.lastname, userId: loginUser._id, email: loginUser.email, role: loginUser.role },
      process.env.JWT_SECRET
    );

    res.cookie('token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'Lax'
    });

    loginUser.lastlogin = new Date();
    await loginUser.save();

    res.status(200).json({ message: 'Login successful', email: loginUser.email });
  } catch (err) {
    res.status(500).json({ message: 'Server error', error: err.message });
  }
};

exports.adminSignIn = async(req, res) => {
  const { inputEmail, inputPassword } = req.body;
  try {
    const loginAdmin = await User.findOne({ email: inputEmail });
    if (!loginAdmin) {
      return res.status(404).json({ message: `No Admin found with email: ${inputEmail}` });
    }

    if (loginAdmin.role === 'user') {
      return res.status(404).json({ message: `Users needs to login through the user portal` });
    }

    const passwordMatch = await bcrypt.compare(inputPassword, loginAdmin.password);
    if (!passwordMatch) {
      return res.status(401).json({ message: 'Password is incorrect' });
    }

    token = jwt.sign(
      { firstname: loginAdmin.firstname, lastname: loginAdmin.lastname, userId: loginAdmin._id, email: loginAdmin.email, role: loginAdmin.role },
      process.env.JWT_SECRET,
      { expiresIn: '1d' }
    );

    res.cookie('token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'Lax'
    });

    loginAdmin.lastlogin = new Date();
    await loginAdmin.save();
    await logAdminAction({ 
      adminname: `${loginAdmin.firstname} ${loginAdmin.lastname}`,
      action: `login`,
      subject: 'Admin',
      subject_identifier: loginAdmin.email
    });
    res.status(200).json({ message: 'Login successful', email: loginAdmin.email });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
  
}

// User Sign-Up
exports.signUp = async (req, res) => {
  const { inputFirstName, inputLastName, inputEmail, inputPassword } = req.body;

  try {
    const emailMatch = await User.findOne({ email: inputEmail });
    if (emailMatch) return res.status(409).json({ error: "User already exists" });

    if (!validatePassword(inputPassword)) {
      return res.status(400).json({
        error: 'Password validation failed',
        details: 'Password must be at least 8 characters and include lowercase, uppercase, number, and special character.'
      });
    }

    const hashedPassword = await bcrypt.hash(inputPassword, 10);
    const verifyToken = jwt.sign(
      { email: inputEmail },
      process.env.JWT_SECRET,
      { expiresIn: '10m' }
    );

    const newUser = new User({
      firstname: inputFirstName,
      lastname: inputLastName,
      email: inputEmail,
      password: hashedPassword,
    });

    await newUser.save();

    const verifyLink = `http://localhost:5173/verify-email?token=${verifyToken}`;
    console.log('User saved. Preparing to send email...');
    await sendEmail(inputEmail, 'Verify Your Email', `<a href="${verifyLink}">Click here to verify</a>`);
    console.log('Email sent!');

    res.status(201).json({ message: "Signup successful. Check your email for verification." });
  } catch (err) {
    console.error("Signup error:", err);  // <-- Full backend trace
    res.status(500).json({ error: "Signup failed", details: err.message });
  }
};


// User logout
exports.logout = async ( _, res) => {
  try { 
    // delete token
    res.cookie('token', '', {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'Lax',
      expires: new Date(0)  
    });
    
    res.status(200).json({ message: 'Logout successful' });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

exports.verifyEmail = async (req, res) => {
  const { token } = req.query;

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    const user = await User.findOne({ email: decoded.email });

    if (!user) return res.status(404).json({ success: false, message: 'User not found' });

    if (user.isverified) {
      return res.status(200).json({ success: true, message: 'Email already verified' });
    }

    user.isverified = true;
    await user.save();

    res.status(200).json({ success: true, message: 'Email verified successfully' });
  } catch (err) {
    if (err.name === 'TokenExpiredError') {
      return res.status(400).json({ success: false, message: 'Verification link has expired' });
    }
    res.status(400).json({ success: false, message: 'Invalid token' });
  }
};



exports.requestPasswordReset = async (req, res) => {
  const { email } = req.body;
  try {
    const user = await User.findOne({ email });
    if (!user) return res.status(404).json({ message: 'Email not registered' });

    const token = jwt.sign({ userId: user._id }, process.env.JWT_SECRET, { expiresIn: '15m' });
    const resetLink = `http://localhost:5173/reset-password-form?token=${token}`;
    const emailBody = `
      <p>To reset your password, click the link below:</p>
      <a href="${resetLink}">Reset Password</a>
      <p>If you didn't request this, you can safely ignore this email.</p>
    `;

    await sendEmail(user.email, 'Reset your password', emailBody);


    res.status(200).json({ message: 'Reset link sent to email' });
  } catch (err) {
    res.status(500).json({ message: 'Error sending reset email', error: err.message });
  }
};

exports.resetPassword = async (req, res) => {
  const { token, newPassword } = req.body;

  if (!validatePassword(newPassword)) {
    return res.status(400).json({
      message: 'Password must be at least 8 characters and include lowercase, uppercase, number, and special character.'
    });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    const user = await User.findById(decoded.userId);

    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    user.password = await bcrypt.hash(newPassword, 10);
    await user.save();

    res.status(200).json({ message: 'Password reset successfully' });
  } catch (err) {
    console.error('Password reset failed:', err);
    res.status(500).json({ message: 'Server error', error: err.message });
  }
};
