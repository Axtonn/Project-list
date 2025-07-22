const mongoose = require("mongoose");

const userSchema = new mongoose.Schema({
  firstname: {
    type: String,
    required: true
  },
  lastname: {
    type: String,
    required: true
  },
  email: {
    type: String,
    required: true
  },
  password: {
    type: String,
    required: true
  },
  lastlogin: {
    type: Date,
    default: null
  },
  registerdate: {
    type: Date,
    default: Date.now
  },
  role: {
    type: String,
    default: 'user'
  },
  isverified: {
    type: Boolean,
    default: false
  },
  verifyToken: {
    type: String,
    default: null
  },

});

module.exports = mongoose.model("User", userSchema);