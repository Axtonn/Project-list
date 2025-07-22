const mongoose = require("mongoose");

const reviewSchema = new mongoose.Schema({
  reviewer: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "User",
    required: true
  },
  rating: {
    type: Number,
    required: true,
    min: 1,
    max: 5
  },
  comment: {
    type: String,
    required: true
  },
  hidden: {
    type: Boolean,
    default: false
  }
});

const listingSchema = new mongoose.Schema({
  title: {
    type: String,
    required: true
  },
  brand: {
    type: String,
    required: true
  },
  image: {
    type: String,
    default: ""
  },
  stock: {
    type: Number,
    required: true,
    min: 0
  },
  seller: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "User",
    required: true
  },
  price: {
    type: Number,
    required: true
  },
  reviews: [reviewSchema],
  disabled: {
    type: Boolean,
    default: false
  }
}, {
  timestamps: true
});

module.exports = mongoose.model("Listing", listingSchema);