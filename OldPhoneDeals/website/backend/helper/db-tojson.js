const fs = require('fs');
const path = require('path');
const mongoose = require("../models/Database");
const user = require('../models/User'); // Adjust path to your User model

async function writeUsersToJsonFile() {
  try {
    const users = await user.find(); 
    const json = JSON.stringify(users, null, 2);
    const filePath = path.join(__dirname, 'users.json');

    fs.writeFileSync(filePath, json, 'utf-8');
    // console.log(`Successfully wrote ${users.length} users to users.json`);
    
    mongoose.disconnect();
  } catch (err) {
    console.error('Error:', err);
  }
}

writeUsersToJsonFile();