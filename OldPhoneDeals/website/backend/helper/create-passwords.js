// This js file is created incase if you want to add passwords to every user, you don't have to use it

const mongoose = require("../models/Database");
const bcrypt = require('bcrypt');
const user = require("../models/User");

function generatePassword(first, last) {
  const f = (first).trim()[0] || 'x';
  const l = (last ).trim()[0] || 'x';
  return `${f}${l}000000`.toLowerCase();
}

const generateHashedPassword = async () => {
  try {
    const users = await user.findAll([]); // get all users from DB

    for (const user of users) {
      const basePassword = generatePassword(user.firstname, user.lastname);
      const hashed = await bcrypt.hash(basePassword, 10);
      user.password = hashed;
      await user.save(); // save updated user
      // console.log(`Updated ${user.email} with password: ${basePassword}`);
    }

    mongoose.disconnect();
  } catch (err) {
    console.error(err);
    mongoose.disconnect();
  }
};

generateHashedPassword();

