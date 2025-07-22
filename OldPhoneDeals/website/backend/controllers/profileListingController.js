const Listing = require('../models/Listing');
const ListingLog = require('../models/ListingLog');
const mongoose = require('mongoose');

exports.createListing = async (req, res) => {
  try {
    let { title, price, stock } = req.body;
    const errors = [];

    // Convert types
    price = Number(price);
    stock = Number(stock);

    // Individual validations
    if (!title || typeof title !== 'string' || title.trim() === '') {
      errors.push('Title must not be empty.');
    }
    if (isNaN(price) || price < 1) {
      errors.push('Price must be a number greater than or equal to 1.');
    }
    if (isNaN(stock) || stock < 1) {
      errors.push('Stock must be a number greater than or equal to 1.');
    }

    if (errors.length > 0) {
      return res.status(400).json({ message: 'Validation error', errors });
    }

    // Escape input to prevent XSS
    title = title.replace(/</g, "&lt;").replace(/>/g, "&gt;");

    let imageBase64 = '';
    if (req.file) {
      imageBase64 = `data:${req.file.mimetype};base64,${req.file.buffer.toString('base64')}`;
    }

    const newListing = new Listing({
      title,
      price,
      stock,
      seller: req.user.userId,
      image: imageBase64,
      brand: 'Generic'
    });

    await newListing.save();

    await ListingLog.create({
      user: req.user.userId,
      listingId: newListing._id,
      title,
      price,
      stock,
      action: 'created'
    });

    res.status(201).json({ message: 'Listing created successfully' });
  } catch (err) {
    res.status(500).json({ message: 'Failed to add listing', error: err.message });
  }
};



exports.getMyListings = async (req, res) => {
  try {
    const listings = await Listing.find({ seller: new mongoose.Types.ObjectId(req.user.userId) });
    res.status(200).json(listings);
  } catch (err) {
    res.status(500).json({ message: 'Failed to fetch user listings', error: err.message });
  }
};

exports.enableListing = async (req, res) => {
  await Listing.findByIdAndUpdate(req.params.id, { disabled: false });
  res.status(200).json({ message: 'Enabled' });
};

exports.disableListing = async (req, res) => {
  await Listing.findByIdAndUpdate(req.params.id, { disabled: true });
  res.status(200).json({ message: 'Disabled' });
};

exports.deleteListing = async (req, res) => {
  const listingId = req.params.id;

  if (!mongoose.Types.ObjectId.isValid(listingId)) {
    return res.status(400).json({ message: 'Invalid ID format' });
  }

  try {
    const listing = await Listing.findById(listingId);
    if (!listing) return res.status(404).json({ message: 'Listing not found' });

    if (
      listing.seller.toString() !== req.user.userId &&
      req.user.role !== 'admin'
    ) {
      return res.status(403).json({ message: 'Forbidden' });
    }

    await Listing.findByIdAndDelete(listingId);

    await ListingLog.create({
      user: req.user.userId,
      listingId: listing._id,
      title: listing.title,
      price: listing.price,
      stock: listing.stock,
      action: 'deleted'
    });


    res.status(200).json({ message: 'Listing deleted' });
  } catch (err) {
    res.status(500).json({ message: 'Server error', error: err.message });
  }
};
