const User = require('../models/User');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const Listing = require('../models/Listing');
const { sendPasswordChangeEmail, sendProfileUpdateEmail } = require('../helper/sendEmail');
const { validatePassword } = require('../helper/validatePassword');

exports.getUserInfo = async (req, res) => {
  try {
    const userId = req.user.userId;
    const currentUser = await User.findById(userId);
    if (!currentUser) {
      return res.status(404).json({ message: 'User not found' });
    }
    return res.status(200).json({
      id: currentUser._id,
      email: currentUser.email,
      firstname: currentUser.firstname,
      lastname: currentUser.lastname,
      role: currentUser.role
    });
  } catch (err) {
    return res.status(500).json({ message: 'Failed to retrieve user data', error: err.message });
  }
};

exports.getUserReviews = async (req, res) => {
  try {
    const userId = req.user.userId;
    const listings = await Listing.find({ seller: userId }).lean();
    
    const data = listings.map(listing => ({
      listingId: listing._id,
      listingTitle: listing.title,
      image: listing.image,
      comments: listing.reviews || []
    }));

    res.json(data);
  } catch (err) {
    res.status(500).json({ message: 'Failed to fetch reviews', error: err.message });
  }
};

exports.updateProfile = async (req, res) => {
  const { firstname, lastname, email, password } = req.body;

  try {
    const decoded = jwt.verify(req.cookies.token, process.env.JWT_SECRET);
    const user = await User.findById(decoded.userId);

    if (!user) return res.status(404).json({ message: 'User not found' });

    const passwordMatch = await bcrypt.compare(password, user.password);
    if (!passwordMatch) return res.status(401).json({ message: 'Invalid password' });

    user.firstname = firstname;
    user.lastname = lastname;
    user.email = email;
    await user.save();

    await sendProfileUpdateEmail(user.email, user.firstname);

    res.status(200).json({ message: 'Profile updated successfully' });
  } catch (err) {
    res.status(500).json({ message: 'Error updating profile', error: err.message });
  }
};


exports.changePassword = async (req, res) => {
  const { currentPassword, newPassword } = req.body;

  try {
    const decoded = jwt.verify(req.cookies.token, process.env.JWT_SECRET);
    const user = await User.findById(decoded.userId);

    const match = await bcrypt.compare(currentPassword, user.password);
    if (!match) {
      return res.status(401).json({ message: 'Current password is incorrect' });
    }

    const isSame = await bcrypt.compare(newPassword, user.password);
    if (isSame) {
      return res.status(400).json({ message: 'New password cannot be the same as the current password' });
    }

    if (!validatePassword(newPassword)) {
      return res.status(400).json({
        message: 'Password must be at least 8 characters and include lowercase, uppercase, number, and special character.'
      });
    }

    user.password = await bcrypt.hash(newPassword, 10);
    await user.save();

    await sendPasswordChangeEmail(user.email, user.firstname);

    res.status(200).json({ message: 'Password updated successfully' });
  } catch (error) {
    console.error("Error changing password:", error);
    return res.status(500).json({
      message: 'Error changing password',
      error: error.message
    });
  }
};



