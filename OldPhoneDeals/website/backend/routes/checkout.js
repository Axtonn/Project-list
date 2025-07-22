const express = require('express');
const router = express.Router();
const checkoutController = require('../controllers/checkoutController');

/* GET */
router.get('/export-sales', checkoutController.exportSales)

/* POST */
router.post('/checkout', checkoutController.checkout)

module.exports = router