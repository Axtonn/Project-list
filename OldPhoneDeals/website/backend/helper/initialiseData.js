const fs = require("fs");
const path = require("path");
const User = require("../models/User");
const Listing = require("../models/Listing");
const { connectToDatabase } = require('../models/Database');

async function loadUsersFromFile(filepath) {
  const rawData = fs.readFileSync(filepath, "utf-8");
  const users = JSON.parse(rawData);
  for (const userData of users) {
    try {
      if (userData._id && typeof userData._id === "object" && userData._id.$oid) {
        userData._id = userData._id.$oid;
      }
      userData.isVerified = true;
      const user = new User(userData);
      await user.save();
    } catch (err) {
      console.error("Failed to save user:", err.message);
    }
  }
  try {
    const adminData = {
      firstname: "Admin",
      lastname: "User",
      email: "admin@example.com",
      password: "$2b$10$LnHZg04A86POMfG1BZoMWu/r1djHmnPZLwVri6sss3M2E4eRrWCqy", //password string is asd
      role: "admin",
      isverified: true,
      lastlogin: null,
      registerdate: new Date()
    };

    const adminUser = new User(adminData);
    await adminUser.save();
    console.log("Admin user added.");
  } catch (err) {
    console.error("Failed to save admin user:", err);
  }
  console.log("Users loaded.");
}

async function loadListingsFromFile(filepath) {
  const rawData = fs.readFileSync(filepath, "utf-8");
  const listings = JSON.parse(rawData);
  for (const listingData of listings) {
    try {
      // Some listing `disabled` fields are ""
      if (typeof listingData.disabled !== 'boolean') {
        delete listingData.disabled;
      }

     // Some review `hidden` fields are ""
      if (Array.isArray(listingData.reviews)) {
        listingData.reviews = listingData.reviews.map(review => {
          if (review.hasOwnProperty("hidden") && review.hidden === "") {
            delete review.hidden;
          }
          return review;
        });
      }

      const listing = new Listing(listingData);
      await listing.save();
    } catch (err) {
      console.error("Failed to save listing:", err);
    }
  }
  console.log("Listings loaded.");
}

async function initialiseDatabase() {
  await connectToDatabase();
  const userCount = await User.countDocuments();
  const listingCount = await Listing.countDocuments();

  if (userCount === 0) {
    console.log("No users found, loading initial data...");
    const userFilePath = path.resolve(__dirname, "../jsondata/userlist.json");
    await loadUsersFromFile(userFilePath);
  }

  if (listingCount === 0) {
    console.log("No listings found, loading initial data...");
    const listingFilePath = path.resolve(__dirname, "../jsondata/phonelisting.json");
    await loadListingsFromFile(listingFilePath);
  }
}
module.exports = { initialiseDatabase };