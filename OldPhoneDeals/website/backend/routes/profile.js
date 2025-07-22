const express = require('express');
const router = express.Router();
const jwt = require('jsonwebtoken');
const profileController = require('../controllers/profileController');
const checkToken = require('../helper/checkToken');

// Routes
router.get('/user-info', checkToken, profileController.getUserInfo);
router.get('/user-reviews', checkToken, profileController.getUserReviews);
router.post('/updateProfile', checkToken, profileController.updateProfile);
router.post('/changePassword', checkToken, profileController.changePassword);

module.exports = router;
