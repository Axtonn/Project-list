const mongoose = require('mongoose');

const salesLogSchema = new mongoose.Schema({
  items: [
    {
      item: { type: String, required: true },
      price: { type: Number, required: true },
      quantity: { type: Number, required: true }
    }
  ],
  totalCost: { type: Number, required: true },
  soldAt: { type: Date, default: Date.now },
  buyerName: { type: String, default: "Unknown" }
});

module.exports = mongoose.model('SalesLog', salesLogSchema);