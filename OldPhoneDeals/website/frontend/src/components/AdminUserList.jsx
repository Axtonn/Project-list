import './AdminUserList.css';
import { useState, useMemo } from 'react';
import axios from 'axios';
import ListingCard from './ListingCard';
import CommentCard from './CommentCard';
import { filterAndSortUsers } from '../utils/filterAndSort';
import { disableUser, activateUser, deleteUser } from '../utils/userApi';
import { disableListing, activateListing, deleteListing } from '../utils/listingApi';
import { disableReview, activateReview, deleteReview } from '../utils/reviewApi';
// import helper api functions from utils

const FloatingWindow = ({
  user, listings, comments, onClose,
  listingDisable, listingActivate, listingDelete, refreshView,
  reviewDisable, reviewActivate, reviewDelete,
  refreshUserView, setSelectedUser
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    firstname: user.firstname,
    lastname: user.lastname,
    email: user.email
  });
  // Allow admin to toggle open editing mode
  const handleEdit = () => setIsEditing(true);
  const handleCancel = () => setIsEditing(false);

  const handleSave = async () => {
    try {
      await axios.put(`http://localhost:3000/api/admin/users/${user._id}`, editForm, {
        withCredentials: true
      });
      alert('User info updated');
      setIsEditing(false);
      setSelectedUser(prev => ({ ...prev, ...editForm }));  // Update selectedUser state
      await fetchUserData();
      await refreshUserView();
    } catch (err) {
      alert('Failed to update user');
    }
  };

  const fetchUserData = async () => {
    try {
      const listingsRes = await axios.get(`http://localhost:3000/api/listings/seller/${user._id}`);
      refreshView(listingsRes.data);
    } catch (error) {
      console.error('Failed to refresh listings or comments:', error);
    }
  };

  return (
    <div className="floating-window">
      <button className="close-btn" onClick={onClose}>X</button>
      <h3>User Info</h3>
      {isEditing ? (
        <>
          <input value={editForm.firstname} onChange={e => setEditForm(f => ({ ...f, firstname: e.target.value }))} />
          <input value={editForm.lastname} onChange={e => setEditForm(f => ({ ...f, lastname: e.target.value }))} />
          <input value={editForm.email} onChange={e => setEditForm(f => ({ ...f, email: e.target.value }))} />
          <button onClick={handleSave}>Save</button>
          <button onClick={handleCancel}>Cancel</button>
        </>
      ) : (
        <>
          <p>{user.firstname} {user.lastname}</p>
          <p>{user.email}</p>
          <button onClick={handleEdit}>Edit User Info</button>
        </>
      )}
      <h3>{user.firstname} {user.lastname}'s Listings</h3>
      {listings.map(listing =>
        <div key={listing._id}>
          <div className="listing-card">
            <ListingCard
              listing={listing}
              preview={true}
              onDisable={() => listingDisable(listing._id)}
              onEnable={() => listingActivate(listing._id)}
              onRemove={() => listingDelete(listing._id)}
            />
          </div>
          <CommentCard
            comments={listing.reviews}
            commentOnly={true}
            adminview={true}
            onDelete={(reviewId) => reviewDelete(reviewId)}
            onShow={(reviewId) => reviewActivate(reviewId)}
            onHide={(reviewId) => reviewDisable(reviewId)}
          />
        </div>
      )}
      <h3>{user.firstname} {user.lastname}'s Comments</h3>
      {(() => {
        const seen = new Set();
        const allUserReviews = [
          ...listings.flatMap(listing =>
            listing.reviews
              .filter(review => String(review.reviewer) === String(user._id))
              .map(review => {
                seen.add(String(review._id));
                return { ...review, listingId: listing._id };
              })
          ),
          ...comments.filter(comment =>
            String(comment.reviewer) === String(user._id) && !seen.has(String(comment._id))
          )
        ];

        return (
          <CommentCard
            comments={allUserReviews}
            showNames={false}
            commentOnly={true}
            adminview={true}
            onDelete={(reviewId) => reviewDelete(reviewId)}
            onShow={(reviewId) => reviewActivate(reviewId)}
            onHide={(reviewId) => reviewDisable(reviewId)}
          />
        );
      })()}
    </div>
  );
};

const UserList = ({ users, refreshUserView }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortKey, setSortKey] = useState('firstname');
  const [sortOrder, setSortOrder] = useState('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedUser, setSelectedUser] = useState(null);
  const [userListings, setUserListings] = useState([]);
  const [userComments, setUserComments] = useState([]);

  const itemsPerPage = 16;

  const fetchUserData = async (user) => {
    try {
      const listingsRes = await axios.get(`http://localhost:3000/api/listings/seller/${user._id}`);
      setUserListings(listingsRes.data);

      const commentRes = await axios.get(`http://localhost:3000/api/users/${user._id}/comments`, {
        withCredentials: true
      });
      setUserComments(commentRes.data);
    } catch (error) {
      console.error('Failed to fetch listings or comments:', error);
    }
  };

  const handleUserClick = async (user) => {
    setSelectedUser(user);
    await fetchUserData(user);
  };

  const handleClose = () => {
    setSelectedUser(null);
    setUserListings([]);
    setUserComments([]);
  };

  const handleUserAction = async (actionFunc, userId) => {
    try {
      await actionFunc(userId);
      await refreshUserView();
    } catch (err) {
      console.error('User action failed:', err);
      alert('Action failed. See console for details.');
    }
  };

  const filteredSortedUsers = useMemo(() =>
    filterAndSortUsers(users, searchTerm, sortKey, sortOrder),
    [users, searchTerm, sortKey, sortOrder]
  );

  const pagedUsers = filteredSortedUsers.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);
  const totalPages = Math.ceil(filteredSortedUsers.length / itemsPerPage);

  const goToPage = (page) => {
    if (page < 1 || page > totalPages) return;
    setCurrentPage(page);
  };

  return (
    <>
      {selectedUser ? (
        <FloatingWindow
          user={selectedUser}
          listings={userListings}
          comments={userComments}
          onClose={handleClose}
          setSelectedUser={setSelectedUser}
          listingDisable={disableListing}
          listingActivate={activateListing}
          listingDelete={deleteListing}
          reviewDelete={deleteReview}
          reviewActivate={activateReview}
          reviewDisable={disableReview}
          refreshView={setUserListings}
          refreshUserView={refreshUserView}
        />
      ) : (
        <>
          <h2>List of Users</h2>
          <input
            type="text"
            placeholder="Search by name or email"
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setCurrentPage(1);
            }}
          />
          <select onChange={(e) => setSortKey(e.target.value)} value={sortKey}>
            <option value="firstname">First Name</option>
            <option value="lastname">Last Name</option>
            <option value="email">Email</option>
            <option value="registerdate">Register Date</option>
            <option value="role">Role</option>
            <option value="isverified">Disabled Login</option>
          </select>
          <select onChange={(e) => setSortOrder(e.target.value)} value={sortOrder}>
            <option value="asc">Asc</option>
            <option value="desc">Desc</option>
          </select>

          <div className="users-container">
            {pagedUsers.map((user) => (
              <div key={user._id} className="user-card" onClick={() => handleUserClick(user)} style={{ cursor: 'pointer' }}>
                <div className="user-info">
                  <div>{user.firstname} {user.lastname}</div>
                  <div>Email: {user.email}</div>
                  <div>Last Login: {user.lastlogin ? new Date(user.lastlogin).toLocaleString() : 'Never'}</div>
                  <div>Register Date: {new Date(user.registerdate).toLocaleString()}</div>
                  <div>Role: {user.role}</div>
                  <div>Enabled: {user.isverified ? 'Yes' : 'No'}</div>
                </div>
                {user.role !== 'admin' && (
                  <div className="user-actions">
                    {user.isverified ? (
                      <button className="disable-button" onClick={(e) => {
                        e.stopPropagation();
                        if (window.confirm("Are you sure you want to DISABLE this user's account?")) {
                          handleUserAction(disableUser, user._id);
                        }
                      }}>Disable</button>
                    ) : (
                      <button className="disable-button" onClick={(e) => {
                        e.stopPropagation();
                        if (window.confirm("Are you sure you want to ENABLE this user's account?")) {
                          handleUserAction(activateUser, user._id);
                        }
                      }}>Enable</button>
                    )}
                    <button className="delete-button" onClick={(e) => {
                      e.stopPropagation();
                      if (window.confirm("Are you sure you want to DELETE this user's account? THIS ACTION IS IRREVERSIBLE!")) {
                        handleUserAction(deleteUser, user._id);
                      }
                    }}>Delete</button>
                  </div>
                )}
              </div>
            ))}
          </div>

          <div style={{ marginTop: '12px' }}>
            <button onClick={() => goToPage(currentPage - 1)} disabled={currentPage === 1}>Prev</button>
            <span> Page {currentPage} of {totalPages} </span>
            <button onClick={() => goToPage(currentPage + 1)} disabled={currentPage === totalPages}>Next</button>
          </div>
        </>
      )}
    </>
  );
};

export default UserList;
