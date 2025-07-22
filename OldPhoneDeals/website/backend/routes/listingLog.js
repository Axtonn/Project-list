const express = require('express');
const router = express.Router();
const ListingLog = require('../models/ListingLog');
const User = require('../models/User');
const jwt = require('jsonwebtoken');

// basic checkAdmin middleware
function checkAdmin(req, res, next) {
  const token = req.cookies.token;
  if (!token) return res.status(401).json({ message: 'Not authenticated' });

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    if (decoded.role !== 'admin') return res.status(403).json({ message: 'Admins only' });
    req.user = decoded;
    next();
  } catch (err) {
    return res.status(403).json({ message: 'Invalid token' });
  }
}

router.get('/logs', checkAdmin, async (req, res) => {
  try {
    const logs = await ListingLog.find().populate('user', 'firstname lastname email').sort({ createdAt: -1 });
    res.json(logs);
  } catch (err) {
    res.status(500).json({ message: 'Failed to fetch logs', error: err.message });
  }
});

module.exports = router;
