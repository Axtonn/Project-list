const mongoose = require("mongoose");

async function connectToDatabase() {
  try {
    await mongoose.connect("mongodb://localhost:27017/ecommerce-database");
    console.log("MongoDB connected");
  } catch (err) {
    console.error("MongoDB connection error:", err);
    process.exit(1);
  }
}

module.exports = { mongoose, connectToDatabase };