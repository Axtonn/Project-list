const express = require('express');
const router = express.Router();
const wishlistController = require('../controllers/wishlistController');
const checkToken = require('../helper/checkToken');


router.get('/wishlist-items', checkToken, wishlistController.getWishlistItems);
router.post('/wishlist', checkToken, wishlistController.addItemToWishlist);
router.delete('/wishlist', checkToken, wishlistController.removeItemFromWishlist);

module.exports = router;