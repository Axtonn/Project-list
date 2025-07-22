const jwt = require('jsonwebtoken');
require('dotenv').config();

const checkToken = (req, res, next) => {
  const token = req.cookies.token;
  if (!token) return res.status(403).json({ message: 'Access Denied' });

  try {
    const verified = jwt.verify(token, process.env.JWT_SECRET);
    req.user = verified;
    next();
  } catch (err) {
    return res.status(403).json({ message: 'Invalid Token' });
  }
};

module.exports = checkToken;
