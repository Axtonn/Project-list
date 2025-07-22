require('dotenv').config();
const express = require('express');
const cors = require("cors");
const path = require('path');
const cookieParser = require('cookie-parser');

const { mongoose, connectToDatabase } = require('./models/Database');
const { initialiseDatabase } = require('./helper/initialiseData');

const app = express();
const PORT = 3000;

app.use(cors({
  origin: 'http://localhost:5173',   // your frontend URL
  credentials: true                  // allow cookies to be sent
}));

// need to import express.json() in order to parse json files
app.use(cookieParser());
app.use(express.json());

const authRoutes = require('./routes/auth');
const listingRoutes = require('./routes/listings');
const userRoutes = require('./routes/user');
const checkoutRoutes = require('./routes/checkout');
const profileRoutes = require('./routes/profile');
const profileListingRoutes = require('./routes/profileListing');
const listingLogRoutes = require('./routes/listingLog');
const wishlistRoutes = require('./routes/wishlist');

app.use('/api', authRoutes);
app.use('/api', userRoutes)
app.use('/api', listingRoutes);
app.use('/api', checkoutRoutes);
app.use('/api', profileRoutes);
app.use('/api/', wishlistRoutes);
app.use('/api/mylistings', profileListingRoutes);
app.use('/api/admin/listing-log', listingLogRoutes);

app.get('/', (req, res) => {
  res.send("Hello, world!")
});

// Serve static files from the React app
app.use(express.static(path.join(__dirname, "..", "client", "public", "src")));

module.exports = app;

async function startServer() {
  try {
    await connectToDatabase();
    await initialiseDatabase();
    app.listen(PORT, () => {
      console.log(`Server running at http://localhost:${PORT}`);
    });
  } catch(e){
    console.error('Failed to start server:', e);
    process.exit(1);
  }
  
}

startServer();