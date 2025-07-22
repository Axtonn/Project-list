import { useState, useEffect } from 'react';
import reactLogo from './assets/react.svg';

import React from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

import starImg from './assets/favicon.ico'; 
import Apple from './assets/Apple.jpeg';
import BlackBerry from './assets/BlackBerry.jpeg';
import HTC from './assets/HTC.jpeg';
import Huawei from './assets/Huawei.jpeg';
import LG from './assets/LG.jpeg';
import Motorola from './assets/Motorola.jpeg';
import Nokia from './assets/Nokia.jpeg';
import Samsung from './assets/Samsung.jpeg'; 
import Sony from './assets/Sony.jpeg';
import Profile from './pages/Profile';


function Home() {
  const navigate = useNavigate();

  const [listings, setListings] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [responseMsg, setResponseMsg] = useState('');

  const [searchQuery, setSearchQuery] = useState('');
  const [filteredListings, setFilteredListings] = useState([]);
  const [showFilters, setShowFilters] = useState(false);

  const [selectedBrand, setSelectedBrand] = useState('All');
  const [maxPrice, setMaxPrice] = useState(1000);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);

  const [soldOutSoon, setSoldOutSoon] = useState([]);
  const [bestSellers, setBestSellers] = useState([]);

  const [selectedItem, setSelectedItem] = useState(null);
  const [selectedSellerName, setSelectedSellerName] = useState('');

  const [committedSearchQuery, setCommittedSearchQuery] = useState('');


  const brandImages = {
    apple: Apple,
    blackberry: BlackBerry,
    htc: HTC,
    huawei: Huawei,
    lg: LG,
    motorola: Motorola,
    nokia: Nokia,
    samsung: Samsung,
    sony: Sony,
  };


  const [showQuantityInput, setShowQuantityInput] = useState(false);
  const [cartQuantity, setCartQuantity] = useState(0); // temporary storing quantity before pressing confirm
  const [wishlistAdded, setWishlistAdded] = useState(false);

  const [expandedComments, setExpandedComments] = useState({});
  const [hiddenComments, setHiddenComments] = useState({});
  const [visibleReviewsCount, setVisibleReviewsCount] = useState(3);

  const [newComment, setNewComment] = useState('');
  const [newRating, setNewRating] = useState(5); 
  const [submitStatus, setSubmitStatus] = useState(null);

  const [reviewerNames, setReviewerNames] = useState({});

  const [availableBrands, setAvailableBrands] = useState([]);


  const [checkingAuth, setCheckingAuth] = useState(true);

  // Cart storage
  const [cart, setCart] = useState(() => {
    const savedCart = localStorage.getItem("cart");
    return savedCart ? JSON.parse(savedCart) : [];
  })

  // Calculates quantity in cart of selected item
  const quantityInCart = selectedItem
  ? (cart.find(ci => ci._id === selectedItem._id)?.quantity || 0)
  : 0;

  // Add to cart after pressing "Confirm" button
  const addToCart = (item, quantity) => {
    if (quantity === 0) {
      //Remove item from cart if quantity is 0
      setCart(prevCart => prevCart.filter(cartItem => cartItem._id !== item._id));
    } else {
      setCart(prevCart => {
        const existingIndex = prevCart.findIndex(cartItem => cartItem._id === item._id);

        if (existingIndex !== -1) {
          // Update quantity
          const updatedCart = [...prevCart];
          updatedCart[existingIndex].quantity = quantity;
          return updatedCart;
        } else {
          // Add new item with quantity
          return [...prevCart, { ...item, quantity }];
        }
      });
    }
  }

  // Saving cart object to local storage whenever cart changes
  useEffect(() => {
    localStorage.setItem("cart", JSON.stringify(cart));
  }, [cart]);

  const fetchData = async (user) => {
    try {
      const res = await axios.get("http://localhost:3000/api/listings", {
        params: { disabled: false },
        withCredentials: true
      });

      setListings(res.data);

      await getBestSellers();
      await getSoldOutSoon();
      if (user) 
        await fetchUserLogin();
    } catch (err) {
      console.error("Failed to fetch listings:", err);
    }
  };

  useEffect(() => {
    fetchData(true);
  }, []);

  const fetchUserLogin = async () => {
    try {
      const response = await axios.get('http://localhost:3000/api/user/user-info', {
        withCredentials: true 
      });
      
      // Fallback if profile is empty or null
      if (!response) {
        throw new Error('Invalid profile data');
      }

      if (response.data && response.data.id) {
        setIsLoggedIn(true);
        setUser(response.data);
      }
      // use this for operations and search
      //console.log(response.data)
    } catch (error) {
      setIsLoggedIn(false);
      console.log('User not Logged in', error);
    } finally {
      setCheckingAuth(false); 
    }
  }

  const getSoldOutSoon = async () => {
    const response = await axios.get('http://localhost:3000/api/listings/sold-out-soon');
    // console.log(response.data)
    if (!response || !response.data)  throw new Error('no solf out seller');

    setSoldOutSoon(response.data);
  };

  const getBestSellers = async () => {
    const response = await axios.get('http://localhost:3000/api/listings/best-sellers');

    if (!response || !response.data) throw new Error('no best seller');

    setBestSellers(response.data);
  };

  const handleSearch = async () => {
    setCommittedSearchQuery(searchQuery); 
    try {
        setSelectedBrand('All');
        setMaxPrice(1000);
      const res = await axios.get("http://localhost:3000/api/listings", {
        params: {
          disabled: false,
          title: searchQuery
        },
        withCredentials: true
      });
  
      setFilteredListings(res.data);
      setShowFilters(true);
    } catch (err) {
      console.error("Search failed:", err);
    }
  };
  

  const handleFilter = () => {
    const filtered = listings.filter(item => {
      const matchesTitle = item.title.toLowerCase().includes(committedSearchQuery.toLowerCase());
      const matchesBrand = selectedBrand === 'All' || item.brand === selectedBrand;
      const matchesPrice = item.price <= maxPrice;
      return matchesTitle && matchesBrand && matchesPrice;
    });
    setFilteredListings(filtered);
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get("http://localhost:3000/api/listings", {
          withCredentials: true
        });
        setListings(res.data);
        
        await getBestSellers()
        await getSoldOutSoon()
        await fetchUserLogin()
        
      } catch (err) {
        console.error("Failed to fetch listings:", err);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    if (showFilters) handleFilter();
  }, [selectedBrand, maxPrice]);

  const handleClearSearch = () => {
    setSearchQuery('');
    setFilteredListings(listings);
    setShowFilters(false);
  };

  const renderStars = (rating) => {
    const fullStars = Math.floor(rating);
    const stars = [];
    for (let i = 0; i < 5; i++) {
      stars.push(
        <span key={i}>
          {i < fullStars ? '⭐' : '☆'}
        </span>
      );
    }
    return <div className="stars">{stars}</div>;
  };

  const getUserFullName = async (item) => {
    try {
      const response = await axios.get("http://localhost:3000/api/user/full-name", {
        params: { id: item.seller },
        withCredentials: true
      });

      setSelectedSellerName(response.data.firstname + ' ' + response.data.lastname);
    } catch (error) {
      console.error("Failed to fetch seller name");
      setSelectedSellerName("Unknown");
    }
  }

  const refreshSelectedItem = async () => {
    try {
      const response = await axios.get(`http://localhost:3000/api/listings/${selectedItem._id}`, {
        withCredentials: true
      });
      setSelectedItem(response.data);
      await fetchReviewerNames(response.data.reviews || []);
    } catch (err) {
      console.error("Failed to refresh selected item:", err);
    }
  };  

  const handleCloseSelectedItem = () => {
    setSelectedItem(null);
    setSubmitStatus(null); 
    setNewComment('');
    setNewRating(5);
    setVisibleReviewsCount(3); 
    setExpandedComments({});
    setHiddenComments({});
    setShowQuantityInput(false);

    fetchData(false);
  };
  

  const renderListingCard = (item) => {
    const avgRating =
      item.reviews && item.reviews.length > 0
        ? item.reviews.reduce((sum, r) => sum + r.rating, 0) / item.reviews.length
        : 0;

    const brandKey = item.brand?.toLowerCase();
    const brandImage = (() => {
      if (item.image?.startsWith('data:image')) return item.image;
      if (item.image && item.image.length > 100) return `data:image/jpeg;base64,${item.image}`;
      return brandImages[brandKey] || 'https://via.placeholder.com/100';
    })();



    return (
      <div
        key={item._id}
        className="listing-card"
        onClick={async () => {
            setSelectedItem(item);
            await getUserFullName(item);
            await fetchReviewerNames(item.reviews || []);
          }}          
        style={{ cursor: 'pointer' }}
      >
        <img src={brandImage} alt={item.title} />
        <div className="listing-info">
          <div className="listing-title">{item.title}</div>
          <div className="listing-price">${item.price}</div>
          <div className="listing-stock">{item.stock} available</div>
          {renderStars(avgRating)}
        </div>
      </div>
    );
  };

  const toggleComment = (index) => {
    setExpandedComments(prev => ({ ...prev, [index]: !prev[index] }));
  };
  
  // handling the hiding of comments
  const handleToggleReviewVisibility = async (reviewId) => {
    try {
      const res = await axios.patch(
        `http://localhost:3000/api/reviews/${selectedItem._id}/${reviewId}/toggle-visibility`,
        {},
        { withCredentials: true }
      );

      const updatedReviews = selectedItem.reviews.map((r) =>
        r._id === reviewId ? { ...r, hidden: res.data.hidden } : r
      );
      setSelectedItem({ ...selectedItem, reviews: updatedReviews });
    } catch (err) {
      console.error("Failed to toggle visibility", err);
    }
  };

  const fetchReviewerNames = async (reviews) => {
    const names = {};
  
    for (const review of reviews) {
      const id = review.reviewer;
      if (!reviewerNames[id]) {
        try {
          const response = await axios.get("http://localhost:3000/api/user/full-name", {
            params: { id },
            withCredentials: true,
          });
          names[id] = response.data.firstname + ' ' + response.data.lastname;
        } catch (err) {
          console.error("Failed to get reviewer name for:", id);
          names[id] = "Unknown";
        }
      }
    }
  
    setReviewerNames(prev => ({ ...prev, ...names }));
  };
  
  
  const handleSubmitReview = async () => {
    if (!newComment.trim()) {
      setSubmitStatus("Comment cannot be empty.");
      return;
    }

    try {
      await axios.post(`http://localhost:3000/api/reviews/${selectedItem._id}`, {
        comment: newComment,
        rating: newRating,
      }, {
        withCredentials: true
      });
  
      setSubmitStatus("Review submitted successfully!");
      setNewComment('');
      setNewRating(5);
      setVisibleReviewsCount(3);

      await refreshSelectedItem();
  
    } catch (error) {
      console.error("Error posting comment:", error);
      setSubmitStatus("Failed to post comment.");
    }
  };

  const fetchBrands = async () => {
    try {
      const res = await axios.get('http://localhost:3000/api/listings/brands');
      setAvailableBrands(['All', ...res.data.brands]);
    } catch (err) {
      console.error("Failed to fetch brands:", err);
    }
  };
  
  useEffect(() => {
    fetchBrands();
  }, []);
  

  return (
    <div className="home-wrapper">
      <div className="header">
        <div className="header-left">
          <h1>OldPhoneDeals</h1>
        </div>

        <div className="header-center">
          <input
            type="text"
            placeholder="Search for a phone"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button onClick={handleSearch}>Search</button>
          <button onClick={handleClearSearch}>Clear</button>
        </div>

        <div className="header-right">
          {/*<button onClick={() => navigate('/checkout')}>Checkout</button>*/}
          <button
            style={{
              padding: '8px 16px',
              backgroundColor: '#f06292',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              marginLeft: '10px',
              cursor: 'pointer'
            }}
            onClick={() => {
              if (!isLoggedIn) {
                alert("Please log in first before checking out.");
              } else {
                navigate('/checkout')
              }
            }}
          >
            Checkout
          </button>
          {!isLoggedIn ? (
            <>
              <button onClick={() => navigate('/auth')}>Login</button>
              <button onClick={() => navigate('/admin')}>Admin Login</button>
            </>
          ) : (
            <>
              <button
                onClick={() => navigate('/wishlist')}
                
              >View Wishlist
              </button>
              <button onClick={() => navigate('/profile')}>Profile</button>
              <button onClick={() => {
                const confirmed = window.confirm("Are you sure you want to log out?");
                if (!confirmed) return;

                axios.post('http://localhost:3000/api/logout', {}, { withCredentials: true })
                  .then(() => {
                    localStorage.removeItem("cart");
                    setCart([]);
                    setIsLoggedIn(false);
                    window.location.href = ''; // redirect to login page after logout
                  })
                  .catch(err => console.error('Logout failed:', err));
              }}>
                  Log out
                </button>
            </>
          )}

        </div>
      </div>

      {!showFilters && !selectedItem && (
        <div className="home-sections">

          <h2>Sold Out soon!</h2>
          {soldOutSoon.map(renderListingCard)}

          <h2>Best Sellers!</h2>
          {bestSellers.map(renderListingCard)}
        </div>
      )}

      {showFilters && !selectedItem && (
        <div className="search-results">
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <label style={{ whiteSpace: 'nowrap' }}>
                    Brand:
                    <select value={selectedBrand} onChange={(e) => setSelectedBrand(e.target.value)} style={{ marginLeft: '8px' }}>
                    {availableBrands.map(brand => (
                        <option key={brand} value={brand}>{brand}</option>
                    ))}
                    </select>
                </label>

                <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    Max Price:
                    <span style={{ display: 'inline-block', minWidth: '50px' }}>${maxPrice}</span>
                    <input
                    type="range"
                    min="0"
                    max="1000"
                    step="10"
                    value={maxPrice}
                    onChange={(e) => setMaxPrice(Number(e.target.value))}
                    style={{ width: '400px' }}
                    />
                </label>
                </div>



            <h2>Search results for "{committedSearchQuery}"</h2>
          {filteredListings.length > 0 ? (
            filteredListings.map(renderListingCard)
          ) : (
            <p>No results found.</p>
          )}
        </div>
      )}

      {selectedItem && (
        <div className="item-detail">
          <h2>{selectedItem.title}</h2>
          <img
            src={brandImages[selectedItem.brand?.toLowerCase()]}
            alt={selectedItem.title}
            style={{ width: '150px', height: '150px', objectFit: 'contain', marginBottom: '16px' }}
          />
          <p><strong>Brand:</strong> {selectedItem.brand}</p>
          <p><strong>Price:</strong> ${selectedItem.price}</p>
          <p><strong>Stock:</strong> {selectedItem.stock} available</p>
          <p><strong>Seller:</strong> {selectedSellerName}</p>

          <h3>Top Reviews</h3>
          {(selectedItem.reviews || []).length === 0 ? (
              <p><i>There are currently no reviews for this item.</i></p>
          ) : (
            (selectedItem.reviews || [])
            .slice(0, visibleReviewsCount)
            .map((r, i) => {
              const isExpanded = expandedComments[i];
              const displayedComment =
                isExpanded || r.comment.length <= 200
                  ? r.comment
                  : r.comment.slice(0, 200) + '...';
                
              const canToggleVisibility =
                user &&
                (
                  user.id === selectedItem.seller || // Listing owner
                  user.id === r.reviewer              // Review author
                );
              
              // If review is hidden and user shouldn't see it, skip it
              if (r.hidden && !canToggleVisibility) {
                return null;
              }

              return (
                <div key={r._id} style={{ marginBottom: '12px' }}>
                  <p><strong>Reviewer:</strong> {reviewerNames[r.reviewer] || "Loading..."}</p>
                  <p><strong>Rating:</strong> {r.rating} ⭐</p>
                  <p style={{ color: r.hidden ? 'gray' : 'black' }}>{displayedComment}</p>

                  {r.comment.length > 200 && (
                    <button
                      onClick={() =>
                        setExpandedComments((prev) => ({ ...prev, [i]: !prev[i] }))
                      }
                      style={{ marginRight: '8px' }}
                    >
                      {isExpanded ? 'Show less' : 'Show more'}
                    </button>
                  )}

                  {canToggleVisibility && (
                    <button
                      onClick={async () => {
                        try {
                          const res = await axios.patch(
                            `http://localhost:3000/api/reviews/${selectedItem._id}/review/${r._id}/toggle-visibility`,
                            {},
                            { withCredentials: true }
                          );
                          const updatedReviews = selectedItem.reviews.map((rev) =>
                            rev._id === r._id ? { ...rev, hidden: res.data.hidden } : rev
                          );
                          setSelectedItem({ ...selectedItem, reviews: updatedReviews });
                        } catch (err) {
                          console.error("Failed to toggle visibility", err);
                        }
                      }}
                    >
                      {r.hidden ? 'Unhide comment' : 'Hide comment'}
                    </button>
                  )}
                </div>
              );
            })
          )}

          {selectedItem.reviews?.length > visibleReviewsCount && (
            <button onClick={() => setVisibleReviewsCount((prev) => prev + 3)}>
              Show more reviews
            </button>
          )}

          <hr style={{ margin: '16px 0', borderColor: 'rgba(0, 0, 0, 0.1)' }} />

                <div style={{ marginTop: '24px' }}>
                <p><strong>In Cart:</strong> {quantityInCart}</p>

                {!showQuantityInput ? (
                  selectedItem.stock === 0 ? (
                    <button disabled style={{ backgroundColor: '#ccc', color: '#666', cursor: 'not-allowed' }}>
                      Out of Stock
                    </button>
                  ) : (
                    <button
                      onClick={() => {
                        if (!isLoggedIn) {
                          alert("Please log in first to add items to your cart.");
                          navigate("/auth");
                        } else {
                          setShowQuantityInput(true);
                        }
                      }}
                    >
                      Add to Cart
                    </button>
                  )
                ) : (
                  <div>
                    <input
                      type="number"
                      min="0"
                      step="1"
                      placeholder="Quantity"
                      onChange={(e) => {
                        let val = Number(e.target.value);
                        setCartQuantity(val);
                      }}
                      style={{
                        marginRight: '8px',
                        height: '26px',
                        padding: '6px 12px',
                        fontSize: '14px',
                        borderRadius: '4px',
                        border: '1px solid #ccc'
                      }}
                    />
                    <button onClick={() => {
                      if (isNaN(cartQuantity)) {
                        alert("Please enter a valid quantity.");
                        return;
                      }

                      if (!Number.isInteger(cartQuantity)) {
                        alert("Quantity must be a whole number.");
                        return;
                      }

                      if (cartQuantity < 1) {
                        alert("Please enter a quantity of at least 1.");
                        return;
                      }

                      if (cartQuantity > selectedItem.stock) {
                        alert(`There are only ${selectedItem.stock} available`);
                        return;
                      }

                      addToCart(selectedItem, cartQuantity);
                      setCartQuantity(0);
                      setShowQuantityInput(false);
                    }}>
                      Confirm
                    </button>
                  </div>
                )}

                <button
                    onClick={async () => {
                      if (!isLoggedIn) {
                        alert("Please log in first to add items to your wishlist.");
                        navigate('/auth');
                      } else {
                        try {
                          await axios.post(
                            'http://localhost:3000/api/wishlist',
                            {
                              userId: user.id,
                              listingId: selectedItem._id,
                            },
                            { withCredentials: true }
                          );

                          setWishlistAdded(true);
                        } catch (err) {
                          console.error("Failed to add to wishlist:", err);
                          alert("Something went wrong while adding to wishlist.");
                        }
                      }
                    }}
                    disabled={wishlistAdded}
                    style={{ marginLeft: '16px' }}
                >
                    {wishlistAdded ? 'Added to Wishlist' : 'Add to Wishlist'}
                </button>
                </div>

          <hr style={{ margin: '24px 0', borderColor: 'rgba(0, 0, 0, 0.1)' }} />
          <h3>Leave a Review</h3>
          <div
            style={{
              marginBottom: '16px',
              opacity: isLoggedIn ? 1 : 0.5,
              pointerEvents: isLoggedIn ? 'auto' : 'none',
            }}
          >
            <textarea
              placeholder="Leave a review here!"
              value={newComment}
              disabled={!isLoggedIn}
              onChange={(e) => {
                const value = e.target.value;
                const safe = value.replace(/<[^>]*>?/gm, '').slice(0, 200);
                setNewComment(safe);
              }}
              rows={4}
              maxLength={200}
              style={{
                width: '100%',
                padding: '8px',
                fontSize: '14px',
                marginBottom: '8px',
              }}
            />
            <small>{200 - newComment.length} characters remaining</small>

            <div style={{ marginBottom: '8px' }}>
              <label><strong>Rating:</strong></label>
              <select
                value={newRating}
                disabled={!isLoggedIn}
                onChange={(e) => setNewRating(Number(e.target.value))}
                style={{ marginLeft: '8px' }}
              >
                {[1, 2, 3, 4, 5].map((n) => (
                  <option key={n} value={n}>{n}</option>
                ))}
              </select>
            </div>

            <button disabled={!isLoggedIn} onClick={handleSubmitReview}>
              Post Comment
            </button>

            {submitStatus && (
              <p style={{ color: 'green', marginTop: '8px' }}>{submitStatus}</p>
            )}
          </div>

          {!isLoggedIn && (
            <p style={{ color: 'red', marginBottom: '16px' }}>
              <i>You must be logged in to post a review.</i>
            </p>
          )}

          <button onClick={handleCloseSelectedItem}>Close</button>
        </div>
      )}

    </div>
  );
}

export default Home;