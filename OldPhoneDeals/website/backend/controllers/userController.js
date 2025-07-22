const User = require('../models/User'); 
const Listing = require('../models/Listing');
const Wishlist = require('../models/Wishlist');
const logAdminAction = require('../helper/logAdmin');

exports.getUserInfo = async (req, res) => {
  try {
    const userId = req.user.userId;
    const currentUser = await User.findById(userId);
    if (!currentUser) {
      return res.status(404).json({ message: 'User not found' });
    }
    //console.log('fetch completed')
    return res.status(200).json({
      id: currentUser._id, // Use _id instead of id as Mongoose adds _id by default
      email: currentUser.email,
      firstname: currentUser.firstname,
      lastname: currentUser.lastname,
      role: currentUser.role
    });

  } catch (err) {
    return res.status(500).json({ message: 'Failed to retrieve user data', error: err.message });
  }
};

exports.getFullName = async (req, res) => {
  try {
    const { id } = req.query;
    const user = await User.findById(id);

    res.json({ firstname: user.firstname, lastname: user.lastname });
  } catch (err) {
    res.status(500).json({ message: 'Failed to retrieve full name' });
  }
}

exports.getFullUserInfo = async (req, res) => {
  try {
    const allUsers = await User.find();
    res.status(200).json(allUsers);

    logAdminAction({
      adminname: `${req.user.firstname} ${req.user.lastname}`,
      action: 'view all users',
      subject: 'User',
      subject_identifier: 'all'
    });
      
  } catch (err) {
    return res.status(500).json({ message: 'Failed to retrieve user data', error: err.message });
  }
}

exports.updateUserInfo = async (req, res) => {
  try {
    const updatedUser = await User.findByIdAndUpdate(
      userId,
      {
        email,
        firstname,
        lastname,
        role
      },
      { new: true } // This ensures the updated document is returned
    );
    if (!updatedUser) {
      return res.status(404).json({ message: 'User not found' });
    }
    
    return res.status(200)
  } catch (err) {
    return res.status(500).json({ message: 'Failed to update user parameter', error: err.message });
  }
}

exports.toggleDisableUser = async (req, res) => {
  try {
    const { action } = req.body;

    if (action !== 'deactivate' && action !== 'activate') {
      return res.status(400).json({ message: 'Invalid action. Use "activate" or "deactivate".' });
    }
    
    const update = action === 'deactivate' ? { isverified: false } : { isverified: true };

    const user = await User.findByIdAndUpdate(
      req.params.id,
      { $set: update },
      { new: true }
    );
    if (!user) {
      return res.status(404).json({ message: `No user found with id: ${req.params.id}` });
    }
    
    await logAdminAction({ 
      adminname: `${req.user.firstname} ${req.user.lastname}`,
      action: `${action} user account`,
      subject: 'User',
      subject_identifier: user.email
    });
      
    res.status(200).json({ message: 'Disable Successful', user });
  } catch (err) {
    res.status(500).json({ message: 'Server error', error: err.message });
  }
};

exports.deleteUser = async (req, res) => {
  try {
    // console.log('yeah')
    const user = await User.findById(req.params.id);
    if (!user) {
      return res.status(404).json({ message: `No user found with id: ${req.params.id}` });
    }
    await User.deleteOne({ _id: req.params.id });
    const { action } = { action: 'deleted' };
    await logAdminAction({ 
      adminname: `${req.user.firstname} ${req.user.lastname}`,
      action: `${action} user account`,
      subject: 'User',
      subject_identifier: user.email
    });
    res.status(200).json({ message: 'Delete Successful', userEmail: user.email });
  } catch (err) {
    res.status(500).json({ message: 'Server error', error: err.message });
  }
};

exports.getUserListingComments = async (req, res) => {
  try {
    const listings = await Listing.find({ seller: req.params.id }).lean();
    const data = listings.flatMap(listing => 
      (listing.reviews || []).filter(r => !r.hidden).map(review => ({
        _id: review._id,
        comment: review.comment,
        rating: review.rating,
        reviewer: review.reviewer,
        listingId: listing._id,
        listingTitle: listing.title,
        image: listing.image
      }))
    );
    res.json(data);
  } catch (err) {
    res.status(500).json({ message: 'Failed to fetch reviews', error: err.message });
  }
};

exports.getUserWishlistItems = async (req, res) => {
  try {
    const { id } = req.params;

    const data = await Wishlist.find({ user: id });
    res.json(data.items);
  } catch (err) {
    res.status(500).json({ message: 'Failed to fetch wishlist', error: err.message });
  }
}

exports.adminUpdateUser = async (req, res) => {
  const { firstname, lastname, email } = req.body;
  try {
    const updated = await User.findByIdAndUpdate(
      req.params.id,
      { firstname, lastname, email },
      { new: true }
    );
    if (!updated) return res.status(404).json({ message: 'User not found' });
    res.status(200).json(updated);
  } catch (err) {
    res.status(500).json({ message: 'Update failed', error: err.message });
  }
};


