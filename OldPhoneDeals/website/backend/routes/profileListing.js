const express = require('express');
const router = express.Router();
const jwt = require('jsonwebtoken');
const multer = require('multer');
const {
  createListing,
  getMyListings,
  enableListing,
  disableListing,
  deleteListing
} = require('../controllers/profileListingController');
const storage = multer.memoryStorage();
const upload = multer({ storage });
const checkToken = require('../helper/checkToken');


router.post('/', checkToken, upload.single('image'), createListing);
router.get('/', checkToken, getMyListings);
router.post('/:id/enable', checkToken, enableListing);
router.post('/:id/disable', checkToken, disableListing);
router.delete('/:id', checkToken, deleteListing);

module.exports = router;
