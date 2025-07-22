const express = require('express');
const router = express.Router();
const jwt = require('jsonwebtoken');
const userController = require('../controllers/userController');
const checkToken = require('../helper/checkToken');
// Add admin/user controller here
// Rule of thumb, use post when frontend is sending stuff to backend
// Use get when backend is sending stuff to frontend
// PS. Post can still send frontend data, but it is primarily obtaining stuff from frontend

router.get('/user/user-info', checkToken, userController.getUserInfo);
router.get('/user/full-name', userController.getFullName);
router.get('/full-user-info', checkToken, checkAdmin, userController.getFullUserInfo);
router.get('/users/:id/comments', userController.getUserListingComments);
router.get('/users/:id/wishlist', userController.getUserWishlistItems);
router.put('/users/:id/toggle-disable', checkToken, checkAdmin, userController.toggleDisableUser);
router.put('/admin/users/:id', checkToken, checkAdmin, userController.adminUpdateUser);

router.delete('/users/:id', checkToken, checkAdmin, userController.deleteUser);

module.exports = router;

// return 401 for unauthorized
// return 403 for Forbidden, is logged in but not admin
// return 500 for serverside error, eg.) backend crashed

function checkAdmin(req, res, next) {
  try{
    if (!req.user || req.user.role !== 'admin') {
      return res.status(403).json({ message: 'Forbidden: Insufficient permissions' });
    }
    const newToken = jwt.sign(
      {
        firstname: req.user.firstname,
        lastname: req.user.lastname,
        userId: req.user.userId,
        email: req.user.email,
        role: req.user.role
      },
      process.env.JWT_SECRET,
      { expiresIn: '1d' }
    );

    res.cookie('token', newToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'Lax'
    });

    next();
  } catch (e){
    return res.status(500).json({ message: 'Unable to check status, please try again later'})
  }
}

