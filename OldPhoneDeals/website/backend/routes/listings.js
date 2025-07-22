const express = require('express');
const router = express.Router();
const listingController = require('../controllers/listingController');
const checkToken = require('../helper/checkToken');


/* GET */
router.get('/listings/sold-out-soon',  listingController.getSoldOutSoon);
router.get('/listings/best-sellers', listingController.getBestSellers);
router.get('/listings/brands', listingController.getActiveBrands);
router.get('/listings', listingController.getAllListings); // Get all listings OR search
router.get('/listings/:id', listingController.getListingById); // Get listing by id
router.get('/comments', listingController.getAllComments);
router.get('/reviewer/:id', listingController.getReviewerNameById);
router.get('/seller/:id', listingController.getSellerNameByListingId);
/* POST */
// Do we need an API call to create a new listing?

// put review on a listing
router.post('/reviews/:id', checkToken, listingController.addReview);

/* PUT */
router.put('/listings/:id', checkToken, listingController.editListingDetails); // Edit any fields for a listing

/* PATCH */
router.patch('/review/:reviewId', checkToken, listingController.setReviewDisabledStatus); // Toggle between enabled and disabled
router.patch('/reviews/:listingId/review/:reviewId/toggle-visibility', checkToken, listingController.toggleReviewVisibility);

/* DELETE */
router.delete('/listings/:id', checkToken, listingController.deleteListing);
router.delete('/review/:reviewId', checkToken, listingController.deleteReviewById);

router.get('/listings/seller/:sellerId', listingController.getListingsBySellerId);

module.exports = router;

