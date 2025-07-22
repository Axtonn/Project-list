const bcrypt = require('bcrypt');
const mongoose = require('../models/Database');
const user = require('../models/User');

async function updateAdminPassword() {
  try {
    let adminUser = await user.findOne({ firstname: 'Admin' });
    
    if (!adminUser) {
      console.log('Admin user not found');
      return mongoose.disconnect();
    }
    // console.log(adminUser.password)
    const hashedPassword = await bcrypt.hash('admin123', 10);

    const result = await user.updateOne(
      { _id: adminUser._id },
      { $set: { password: hashedPassword } }
    );
    const isMatch = await bcrypt.compare('admin123', adminUser.password)
    // console.log(isMatch)
    // console.log(`Password for ${adminUser.email} successfully updated.`);
    adminUser = await user.findOne({ firstname: 'Admin' });
    // console.log(adminUser.password)
    mongoose.disconnect();
  } catch (err) {
    console.error('Error updating password:', err);
    mongoose.disconnect();
  }
}

updateAdminPassword()
