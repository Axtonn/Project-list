const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');

// add auth related cibtrikker cakk
router.get('/verify-email', authController.verifyEmail);
router.post('/sign-in', authController.signIn);
router.post('/admin-sign-in', authController.adminSignIn);
router.post('/sign-up', authController.signUp);
router.post('/logout', authController.logout)
router.post('/request-password-reset', authController.requestPasswordReset);
router.post('/reset-password', authController.resetPassword);
module.exports = router;