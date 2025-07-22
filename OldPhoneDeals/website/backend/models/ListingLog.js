const mongoose = require("mongoose");

const listingLogSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "User",
    required: true
  },
  title: String,
  price: Number,
  stock: Number,
  createdAt: {
    type: Date,
    default: Date.now
  },
  listingId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "Listing",
    required: true
  },
  action: {
    type: String,
    enum: ['created', 'deleted'],
    required: true
  }
});


module.exports = mongoose.model("ListingLog", listingLogSchema);
// This schema is used to log the changes made to listings. 
