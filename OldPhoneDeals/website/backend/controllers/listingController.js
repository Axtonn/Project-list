const Listing = require('../models/Listing')
const { mongoose } = require('../models/Database');
const User = require('../models/User');
const logAdminAction = require('../helper/logAdmin');
//############################//
//            GET             //
//############################//

exports.getListingsBySellerId = async (req, res) => {
  const { sellerId } = req.params;
  //console.log(req.user.role)
  try {
    const listings = await Listing.find({ seller: sellerId });
    
    if (req.user && req.user.role === 'admin') {
      await logAdminAction({
        adminname: `${req.user.firstname} ${req.user.lastname}`,
        action: 'View listing profile',
        subject: sellerId,
        subject_identifier: sellerId
      });
    }
    res.json(listings);
  } catch (error) {
    //console.error('Failed to fetch listings by seller ID:', error);
    res.status(500).json({ message: 'Server error' });
    //no error needed, it is expected
  }
};

exports.getSellerNameByListingId = async (req, res) => {
  try {
    const { id } = req.params;

    const listing = await Listing.findById(id).populate('seller', 'firstname lastname');
    if (!listing || !listing.seller) {
      //return res.status(404).json({ message: 'Seller not found for this listing' });
    }

    const { firstname, lastname } = listing.seller;

    res.json({ fullname: `${firstname} ${lastname}` });
  } catch (error) {
    //console.error('Error fetching seller name by listing ID:', error);
    //res.status(500).json({ message: 'Internal server error' });
  }
};

exports.getAllListings = async (req, res) => {
  try {
    const { title, brand, disabled} = req.query;

    const query = {};

    if (disabled !== undefined) {
      query.disabled = disabled === 'true'; // convert from string to boolean
    }

    if (title) {
      query.title = { $regex: title, $options: 'i' };
    }

    if (brand) {
      query.brand = { $regex: brand, $options: 'i' };
    }

    const listings = await Listing.find(query);
    res.json(listings);
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch listings" });
  }
};

exports.getListingById = async (req, res) => {
  try {
    const { id } = req.params;
    const listing = await Listing.findById(id);
    
    if (!listing) {
      return res.status(404).json({ error: "Listing not found" });
    }

  } catch {
    res.status(500).json({ error: "Failed to fetch listing by id" });
  }
}

exports.getSoldOutSoon = async (req, res) => {
  // Return the 5 phone listings with the least 
  // non-zero quantity available that are not disabled.

  try {
    const listings = await Listing.find({
      "disabled": false,
      "stock": { $gt: 0 }
    })
      .sort({ stock: 1})
      .limit(5);

    res.json(listings); 
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch listing by id" });
  }
}

exports.getBestSellers = async (req, res) => {
  try {
    // Return the 5 phone listings with the highest average rating.
    
    // Highest average rating is calculated using all listings which are
    // a) not disabled
    // b) have at least two ratings
    // For these listings, we calculate the average rating using ALL ratings
    // regardless of whether the rating is hidden or not.

    // 1. Get all listings which are not disabled and have SOME ratings
    const enabledListings = await Listing.find({
      "disabled": false,
      "reviews": { $exists: true, $not: { $size: 0 }}
    })

    // 2. Filter down to listings with at least 2 reviews
    const reviewedListings = enabledListings.filter(listing => listing.reviews.length >= 2);

    // 3. For each listing, go through all the reviews and calculate its average rating
    for (const listing of reviewedListings) {
      let totalRating = 0;
      let numReviews = 0;

      for (const review of listing.reviews) {
        totalRating += review.rating;
        numReviews++;
      }

      const avgRating = totalRating/numReviews;
      listing.avgRating = avgRating;
    }

    // 4. Sort by highest avgRating
    const sortedByRating = reviewedListings.sort((a, b) => b.avgRating - a.avgRating);

    // 5. Take top 5
    const topFive = sortedByRating.slice(0, 5);
    res.json(topFive);
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch listing by id" });
  }
}

exports.getActiveBrands = async (req, res) => {
  // Get a list of all the brands which are in the catalog
  // (active items only)
  try {
    const listings = await Listing.find(
      { "disabled": false },
      'brand'
    );

    const brands = [...new Set(listings.map((listing) => listing.brand))];
    res.json({ brands: brands }); 
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch listing by id" });
  }
}

exports.getAllComments = async (req, res) => {
  try {
    const listings = await Listing.find({}, 'title brand reviews')
      .populate('reviews.reviewer', 'firstname lastname');

    const allComments = [];

    listings.forEach(listing => {
      listing.reviews.forEach(review => {
        // Skip if reviewer is missing
        if (!review.reviewer) return;

        allComments.push({
          _id: review._id,
          comment: review.comment,
          rating: review.rating,
          hidden: review.hidden,
          listingId: listing._id,
          listingTitle: listing.title,
          listingBrand: listing.brand,
          reviewer: {
            _id: review.reviewer._id,
            firstname: review.reviewer.firstname,
            lastname: review.reviewer.lastname
          }
        });
      });
    });

    res.status(200).json(allComments);
  } catch (error) {
    console.error('Error fetching comments:', error);
    res.status(500).json({ message: 'Failed to fetch comments', error: error.message });
  }
};

exports.getReviewerNameById = async (req, res) => {
  try {
    const reviewerId = req.params.reviewerId;

    // Validate ID
    if (typeof reviewerId !== 'string' || !reviewerId.match(/^[0-9a-fA-F]{24}$/)) {
      return res.status(400).json({ message: 'Invalid reviewer ID' });
    }

    const user = await User.findById(reviewerId).select('firstname lastname');

    if (!user) {
      return res.status(404).json({ message: 'Reviewer not found' });
    }

    res.status(200).json(user);
  } catch (err) {
    console.error('Error fetching reviewer name:', err);
    res.status(500).json({ message: 'Server error' });
  }
};
//############################//
//            POST            //
//############################//



//############################//
//            PUT             //
//############################//

exports.editListingDetails = async (req, res) => {
  try {
    // 1. Get the listing the client wants to edit
    const { id } = req.params;

    // 2. Get the updated fields of the listing
    const updatedData = req.body;

    // 3. Update it and save in database
    const updatedListing = await Listing.findByIdAndUpdate(
      id,
      updatedData,
      { new: true }
    )
    if (req.user.role === 'admin') {
      await logAdminAction({
        adminname: `${req.user.firstname} ${req.user.lastname}`,
        action: 'updated listing',
        subject: 'Listing',
        subject_identifier: id
      });
    }
    if (!updatedListing) {
      return res.status(404).json({ error: "Listing not found" });
    }

    // 4. Return OK code and the updated listing
    res.status(200).json(updatedListing)
  } catch (err) {
    res.status(500).json({ error: "Failed to edit listing" });
  }
}

//############################//
//           PATCH            //
//############################//

exports.toggleEnabledListing = async (req, res) => {
  try {
    const { id } = req.params;
    const { disabled } = req.body;

    if (typeof disabled !== 'boolean') {
      return res.status(400).json({ error: "`disabled` must be true or false." });
    }

    const updatedListing = await Listing.findByIdAndUpdate(
      id,
      { disabled },
      { new: true }
    );

    if (!updatedListing) {
      return res.status(404).json({ error: "Listing not found" });
    }
    if (req.user.role === 'admin') {
      await logAdminAction({
        adminname: `${req.user.firstname} ${req.user.lastname}`,
        action: `toggled listing status to ${disabled}`,
        subject: 'Listing',
        subject_identifier: reviewId
      });
    }
    res.status(200).json(updatedListing);

  } catch (err) {
    console.error('Toggle listing error:', err);
    res.status(500).json({ error: "Failed to update listing status" });
  }
};

//############################//
//           DELETE           //
//############################//

exports.deleteListing = async (req, res) => {
  try {
    const { id } = req.params;

    const deleted = await Listing.findByIdAndDelete(id);
    if (!deleted) {
      return res.status(404).json({ error: "Listing not found" });
    }
    if (req.user.role === 'admin') {
      logAdminAction({
        adminname: `${req.user.firstname} ${req.user.lastname}`,
        action: 'deleted listing',
        subject: 'Listing',
        subject_identifier: id
      });
    }
    res.status(200).json({ message: "Listing deleted" });
  } catch (err) {
    res.status(500).json({ error: "Failed to delete listing" });
  }
}

// add review method to listing
exports.addReview = async (req, res) => {
  const { id } = req.params;
  let { rating, comment } = req.body;
  const reviewer = req.user?.userId;

  if (!reviewer) return res.status(401).json({ error: 'Unauthorized' });

  // Basic input validation
  if (typeof comment !== 'string' || comment.trim() === '') {
    return res.status(400).json({ error: 'Comment is required.' });
  }

  if (comment.length > 200) {
    return res.status(400).json({ error: 'Comment must be 200 characters or fewer.' });
  }

  // Strip basic HTML tags (if needed)
  comment = comment.replace(/<[^>]*>?/gm, '');

  const listing = await Listing.findById(id);
  if (!listing) return res.status(404).json({ error: 'Listing not found' });

  listing.reviews.push({ rating, comment, reviewer });
  await listing.save();

  res.status(200).json({ message: 'Review added successfully' });
};



// add hidden/show review method to listing
exports.toggleReviewVisibility = async (req, res) => {
  try {
    const { listingId, reviewId } = req.params;

    const listing = await Listing.findById(listingId);
    if (!listing) return res.status(404).json({ message: "Listing not found" });

    const review = listing.reviews.id(reviewId);
    if (!review) return res.status(404).json({ message: "Review not found" });

    review.hidden = !review.hidden;
    await listing.save();
    // console.log(req.user.role)
    if (req.user.role === 'admin') {
      await logAdminAction({
        adminname: `${req.user.firstname} ${req.user.lastname}`,
        action: `toggled review status to ${review.hidden}`,
        subject: 'Review',
        subject_identifier: reviewId
      });
    }
    
    res.status(200).json({ message: "Review visibility toggled", hidden: review.hidden });
  } catch (err) {
    res.status(500).json({ message: "Server error", error: err.message });
  }
};

exports.deleteReviewById = async (req, res) => {
  const { reviewId } = req.params;

  if (!mongoose.Types.ObjectId.isValid(reviewId)) {
    return res.status(400).json({ message: "Invalid review ID" });
  }

  try {
    const listing = await Listing.findOne({ "reviews._id": reviewId });

    if (!listing) {
      return res.status(404).json({ message: "Listing with review not found" });
    }

    // Find the index of the review to remove
    const reviewIndex = listing.reviews.findIndex(r => r._id.toString() === reviewId);
    if (reviewIndex === -1) {
      return res.status(404).json({ message: "Review not found in listing" });
    }
    if (req.user.role === 'admin') {
      await logAdminAction({
        adminname: `${req.user.firstname} ${req.user.lastname}`,
        action: `deleted review`,
        subject: 'Review',
        subject_identifier: reviewId
      });
    }
    // Remove the review from the array
    listing.reviews.splice(reviewIndex, 1);

    // Save the updated listing
    await listing.save();
    
    res.json({ message: "Review deleted successfully" });
  } catch (err) {
    console.error("Server error while deleting review:", err);
    res.status(500).json({ message: "Failed to delete review", error: err.message });
  }
};

exports.setReviewDisabledStatus = async (req, res) => {
  const { reviewId } = req.params;
  const { hidden } = req.body;

  if (!mongoose.Types.ObjectId.isValid(reviewId)) {
    return res.status(400).json({ message: "Invalid review ID" });
  }

  if (typeof hidden !== 'boolean') {
    return res.status(400).json({ message: "'hidden' must be a boolean" });
  }

  try {
    const listing = await Listing.findOne({ "reviews._id": reviewId });
    if (!listing) {
      return res.status(404).json({ message: "Listing with review not found" });
    }

    const review = listing.reviews.id(reviewId);
    if (!review) {
      return res.status(404).json({ message: "Review not found in listing" });
    }

    if (req.user.role === 'admin') {
      await logAdminAction({
        adminname: `${req.user.firstname} ${req.user.lastname}`,
        action: `toggled review status to ${review.hidden}`,
        subject: 'Review',
        subject_identifier: reviewId
      });
    }

    review.hidden = hidden;
    await listing.save();

    res.json({ message: `Review is now ${hidden ? 'hidden' : 'visible'}`, hidden: review.hidden });
  } catch (err) {
    console.error("Error updating review hidden status:", err);
    res.status(500).json({ message: "Server error", error: err.message });
  }
};