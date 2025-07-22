import React from 'react';
import './ListingCard.css';

const ListingCard = ({ preview=false, noimage=false, listing, onEnable, onDisable, onRemove }) => {
  // Generate star rating display (5 stars with filled/unfilled)
  const renderRating = (rating) => {
    const stars = [];
    const fullRating = Math.floor(rating);
    for (let i = 0; i < 5; i++) {
      stars.push(
        <span key={i} className={`star ${i < fullRating ? 'filled' : ''}`}>★</span>
      );
    }
    return <div className="rating">{stars}</div>;
  };

  return (
    <div className="listing-card">
      {!preview ?
        <div className="listing-select">
          <input type="radio" name="listing-select" />
        </div> 
      : ''}
      {!noimage &&
        <div className="listing-image">
          {listing.image ? (
            <img src={listing.image} alt={listing.title} />
          ) : (
            <div style={{ width: '100%', height: '100%', background: '#eee', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', color: '#555' }}>
              No image
            </div>
          )}
        </div>
      }

      <div className="listing-name">
        <h4>{listing.title || 'PHONE LISTING NAME'}</h4>
        <div
          className={`listing-status ${listing.disabled ? 'disabled' : 'enabled'}`}
        >
          {listing.disabled ? 'Disabled' : 'Enabled'}
        </div>
      </div>
      <div className="listing-price">
        <p>Price</p>
        <span>${listing.price}</span>
      </div>
      <div className="listing-quantity">
        <p>Stock</p>
        <span>{listing.stock}</span>
      </div>
      <div className="listing-rating">
        {renderRating(listing.rating || 0)}
      </div>
      <div className="listing-actions">
        {listing.disabled ? (
          <button className="action-button" onClick={onEnable}>Enable</button>
        ) : (
          <button className="action-button" onClick={onDisable}>Disable</button>
        )}
        <button className="action-button" onClick={onRemove}>Remove</button>
      </div>
    </div>
  );
};

export default ListingCard;
