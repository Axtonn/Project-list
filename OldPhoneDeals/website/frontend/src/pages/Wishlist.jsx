import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './Profile.css'; // reuse styling
import Apple from '../assets/Apple.jpeg';
import BlackBerry from '../assets/BlackBerry.jpeg';
import HTC from '../assets/HTC.jpeg';
import Huawei from '../assets/Huawei.jpeg';
import LG from '../assets/LG.jpeg';
import Motorola from '../assets/Motorola.jpeg';
import Nokia from '../assets/Nokia.jpeg';
import Samsung from '../assets/Samsung.jpeg';
import Sony from '../assets/Sony.jpeg';
import { jwtDecode } from 'jwt-decode';

const Wishlist = () => {
  const [wishlistItems, setWishlistItems] = useState([]);
  const navigate = useNavigate();
  const token = document.cookie.split('; ').find(row => row.startsWith('token='))?.split('=')[1];
  const userId = token ? jwtDecode(token).userId : null;
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

const getListingImage = (item) => {
  const brandKey = item.brand?.toLowerCase();
  if (item.image?.startsWith('data:image')) return item.image;
  if (item.image && item.image.length > 100) return `data:image/jpeg;base64,${item.image}`;
  return brandImages[brandKey] || 'https://via.placeholder.com/100';
};


  const fetchWishlist = async () => {
    try {
      const res = await axios.get('http://localhost:3000/api/wishlist-items', { withCredentials: true });
      setWishlistItems(res.data);
    } catch (err) {
      console.error('Failed to fetch wishlist:', err);
    }
  };

  const removeFromWishlist = async (listingId) => {
    try {
      await axios.delete('http://localhost:3000/api/wishlist', {
        data: { 
            userId,
            listingId 
        },
        withCredentials: true
      });
      setWishlistItems(prev => prev.filter(item => item._id !== listingId));
    } catch (err) {
      console.error('Failed to remove item:', err);
    }
  };

  useEffect(() => {
    fetchWishlist();
  }, []);

  return (
    <div className="profile-content">
      <div className="profile-tab-wrapper">
        
        <div className="wishlist-page">
            <div className="wishlist-header">
                <button className="back-home-button" onClick={() => navigate('/')}>
                    Back to Home
                </button>
                <h3>My Wishlist</h3>
            </div>
        {wishlistItems.length === 0 ? (
          <p className="no-listings">Your wishlist is empty.</p>
        ) : (
          <div className="listings-container">
            {wishlistItems.map(item => (
              <div key={item._id} className="listing-card" style={{ display: 'flex', alignItems: 'center', marginBottom: '20px' }}>
                <img
                    src={getListingImage(item)}
                    alt={item.title}
                    style={{ width: '100px', height: '100px', objectFit: 'cover', marginRight: '20px' }}
                />
                <div style={{ flexGrow: 1 }}>
                  <h4>{item.title}</h4>
                  <p>${item.price}</p>
                </div>
                <button className="action-button" onClick={() => removeFromWishlist(item._id)}>Remove</button>
              </div>
            ))}
          </div>
        )}
        </div>
      </div>
    </div>
  );
};

export default Wishlist;
