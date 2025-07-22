

const mongoose = require("../models/Database");
const user = require("../models/User");

const generateRoles = async () => {
  try {
    const users = await user.find(); // get all users from DB
    for (const u of users) {
      u.role = 'user';
      await u.save();
      // console.log(`Updated ${u.email} with role: ${u.role}`);
    }

    mongoose.disconnect();
  } catch (err) {
    console.error('Error:', err);
    mongoose.disconnect();
  }
};

generateRoles();

