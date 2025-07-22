import { useState, useMemo, useEffect} from 'react';
import './AdminListingList.css';
import {
  disableListing,
  activateListing,
  deleteListing,
  updateListing
} from '../utils/listingApi';
import { filterAndSortListings } from '../utils/filterAndSort';
import CommentCard from './CommentCard';
import { disableReview, activateReview, deleteReview } from '../utils/reviewApi';
import axios from 'axios';

const AdminListingList = ({ listings, refreshView }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortKey, setSortKey] = useState('title');
  const [sortOrder, setSortOrder] = useState('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;
  const [sellerNames, setSellerNames] = useState({});
  const [editableListings, setEditableListings] = useState({});
  const handleListingAction = async (actionFunction, listingId) => {
    try {
      await actionFunction(listingId);
      await refreshView();
    } catch (error) {
      console.error('Failed to perform listing action:', error);
    }
  };

  const handleReviewAction = async (actionFunction, reviewId) => {
    try {
      await actionFunction(reviewId);
      await refreshView();
    } catch (error) {
      console.error('Failed to perform review action:', error);
    }
  };

  const handleFieldChange = (listingId, field, value) => {
    setEditableListings(prev => ({
      ...prev,
      [listingId]: {
        ...listings.find(l => l._id === listingId),
        ...prev[listingId],
        [field]: value
      }
    }));
  };

  const handleSave = async (listingId) => {
    try {
      await updateListing(listingId, editableListings[listingId]);
      setEditableListings(prev => {
        const updated = { ...prev };
        delete updated[listingId];
        return updated;
      });
      await refreshView();
    } catch (error) {
      console.error('Failed to update listing:', error);
    }
  };

  const filteredSortedListings = useMemo(() =>
    filterAndSortListings(listings, searchTerm, sortKey, sortOrder),
    [listings, searchTerm, sortKey, sortOrder]
  );

  const pagedListings = filteredSortedListings.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);
  const totalPages = Math.ceil(filteredSortedListings.length / itemsPerPage);

  const goToPage = (page) => {
    if (page < 1 || page > totalPages) return;
    setCurrentPage(page);
  };

  useEffect(() => {
    const fetchSellerNames = async () => {
      const names = {};
      try {
        const responses = await Promise.allSettled(
          listings.map(listing =>
            axios.get(`http://localhost:3000/api/seller/${listing._id}`, {
              withCredentials: true
            })
          )
        );

        responses.forEach((result, index) => {
          const listingId = listings[index]._id;
          if (result.status === 'fulfilled') {
            names[listingId] = result.value.data.fullname;
          } else {
            names[listingId] = 'Unknown Seller';
          }
        });
        setSellerNames(names);
      } catch (err) {
        console.error('Error fetching seller names:', err);
      }
    };

    if (listings.length > 0) fetchSellerNames();
  }, [listings]);
  // editable listing with comments attached
  return (
    <>
      <h2>List of Listings</h2>

      <div style={{ marginBottom: '12px' }}>
        <input
          type="text"
          placeholder="Search by title or brand"
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setCurrentPage(1);
          }}
        />
        <select onChange={(e) => setSortKey(e.target.value)} value={sortKey}>
          <option value="title">Title</option>
          <option value="brand">Brand</option>
          <option value="stock">Stock</option>
          <option value="price">Price</option>
          <option value="disabled">Disabled Status</option>
        </select>
        <select onChange={(e) => setSortOrder(e.target.value)} value={sortOrder}>
          <option value="asc">Asc</option>
          <option value="desc">Desc</option>
        </select>
      </div>

      <div className="listings-container">
        {pagedListings.map((listing) => {
          const edit = editableListings[listing._id] || listing;

          return (
            <div key={listing._id} className="wide-container">
              <h2 style={{ color: 'black' }}>
                {sellerNames[listing._id] || listing.seller}
              </h2>
              <p style={{ color: listing.disabled ? 'red' : 'green' }}>
                Status: {listing.disabled ? 'Disabled' : 'Active'}
              </p>
              <div className="listing-card">
                <label>Title:
                  <input
                    value={edit.title || ''}
                    onChange={(e) => handleFieldChange(listing._id, 'title', e.target.value)}
                  />
                </label>
                <label>Brand:
                  <input
                    value={edit.brand || ''}
                    onChange={(e) => handleFieldChange(listing._id, 'brand', e.target.value)}
                  />
                </label>
                <label>Price:
                  <input
                    type="number"
                    value={edit.price ?? ''}
                    onChange={(e) => handleFieldChange(listing._id, 'price', Number(e.target.value))}
                  />
                </label>
                <label>Stock:
                  <input
                    type="number"
                    value={edit.stock ?? ''}
                    onChange={(e) => handleFieldChange(listing._id, 'stock', parseInt(e.target.value, 10) || 0)}
                  />
                </label>
                <div style={{ marginTop: '10px' }}>
                  <button onClick={() => handleSave(listing._id)}>Save</button>
                  {listing.disabled ? (
                    <button onClick={() => handleListingAction(activateListing, listing._id)}>Enable</button>
                  ) : (
                    <button onClick={() => handleListingAction(disableListing, listing._id)}>Disable</button>
                  )}
                  <button onClick={() => handleListingAction(deleteListing, listing._id)}>Delete</button>
                </div>
              </div>

              <CommentCard
                showNames={false}
                comments={listing.reviews || []}
                commentOnly={true}
                adminview={true}
                onDelete={(reviewId) => handleReviewAction(deleteReview, reviewId)}
                onShow={(reviewId) => handleReviewAction(activateReview, reviewId)}
                onHide={(reviewId) => handleReviewAction(disableReview, reviewId)}
              />
            </div>
          );
        })}
      </div>

      <div style={{ marginTop: '12px' }}>
        <button onClick={() => goToPage(currentPage - 1)} disabled={currentPage === 1}>Prev</button>
        <span> Page {currentPage} of {totalPages} </span>
        <button onClick={() => goToPage(currentPage + 1)} disabled={currentPage === totalPages}>Next</button>
      </div>
    </>
  );
};

export default AdminListingList;
