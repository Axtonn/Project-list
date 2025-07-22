const Wishlist = require('../models/Wishlist');
const Listing = require('../models/Listing');

exports.getWishlistItems = async (req, res) => {
  try {
    const userId = req.user?.userId;
    if (!userId) return res.status(401).json({ message: 'Unauthorized' });

    const wishlist = await Wishlist.findOne({ user: userId }).populate('items');
    res.json(wishlist ? wishlist.items : []);
  } catch (err) {
    console.error('❌ Error fetching wishlist:', err);
    res.status(500).json({ message: 'Failed to load wishlist' });
  }
};



exports.addItemToWishlist = async (req, res) => {
  try {
    const { listingId } = req.body;
    const userId = req.user.userId; // ✅ from token

    if (!userId || !listingId) {
      return res.status(400).json({ message: 'Missing userId or listingId' });
    }
    // console.log("User from token:", req.user);

    let wishlist = await Wishlist.findOne({ user: userId });

    if (!wishlist) {
      wishlist = new Wishlist({ user: userId, items: [listingId] });
    } else if (!wishlist.items.includes(listingId)) {
      wishlist.items.push(listingId);
    }

    await wishlist.save();
    res.status(200).json({ message: 'Item added to wishlist', wishlist });
  } catch (error) {
    console.error("Failed to add item to wishlist:", error);
    res.status(500).json({ message: 'Server error' });
  }
};


exports.removeItemFromWishlist = async (req, res) => {
  try {
    const userId = req.user.userId;
    const { listingId } = req.body;

    if (!userId || !listingId) {
      return res.status(400).json({ message: 'Missing userId or listingId' });
    }

    const wishlist = await Wishlist.findOne({ user: userId });
    if (!wishlist) {
      return res.status(404).json({ message: 'Wishlist not found' });
    }

    const index = wishlist.items.indexOf(listingId);
    if (index === -1) {
      return res.status(404).json({ message: 'Item not found in wishlist' });
    }

    wishlist.items.splice(index, 1);
    await wishlist.save();

    res.status(200).json({ message: 'Item removed from wishlist', wishlist });
  } catch (error) {
    console.error("Failed to remove item from wishlist:", error);
    res.status(500).json({ message: 'Server error' });
  }
};
