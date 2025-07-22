const mongoose = require("../models/Database");
const user = require('../models/User');
const bcrypt = require('bcrypt');

async function checkPassword() {
  try {
    const adminUser = await user.findOne({ firstname: 'Admin' }); 
    if (!adminUser) {
      console.log('Admin user not found');
      return mongoose.disconnect();
    }
    const isMatch = await bcrypt.compare('admin123', adminUser.password)
    // console.log('Stored hash:', adminUser.password);
    // console.log(isMatch)
    mongoose.disconnect();
  } catch (err) {
    console.error('Error:', err);
  }
}
checkPassword()