import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import ListingCard from '../components/ListingCard';
import CommentCard from '../components/CommentCard';
import PasswordPrompt from '../components/PasswordPrompt';
import EmailNotification from '../components/EmailNotification';
import './Profile.css';

const Profile = () => {
  const [tab, setTab] = useState('edit');
  const [user, setUser] = useState({ firstname: '', lastname: '', email: '', id: '' });
  const [newProfile, setNewProfile] = useState(user);
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [listings, setListings] = useState([]);
  const [comments, setComments] = useState([]);
  const [showPasswordPrompt, setShowPasswordPrompt] = useState(false);
  const [hideComments, setHideComments] = useState(false);
  const [showNotification, setShowNotification] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchUserData();
    fetchListings();
    fetchComments();
  }, []);

  const fetchUserData = async () => {
    try {
      const response = await axios.get('http://localhost:3000/api/user-info', {
        withCredentials: true // send cookie with request
      });
      console
      // Fallback if profile is empty or null
      if (!response || !response.data) throw new Error('Invalid profile data');
      
      if (response.data.role === 'admin') {
        alert("Admin can't access this page")
        navigate('/')
      } 
      setUser(response.data);
      setNewProfile({
        firstname: response.data.firstname || '',
        lastname: response.data.lastname || '',
        email: response.data.email || '',
      });

    } catch (error) {
      console.error("Error fetching user data:", error);
      alert('Session invalid. Redirecting to home...');
      navigate('/');
    }
  };

  const fetchListings = async () => {
    try {
      const res = await axios.get('http://localhost:3000/api/mylistings', {withCredentials: true});
      setListings(res.data);
    } catch (err) {
      console.error('Failed to fetch listings:', err);
    }
  };

  const fetchComments = async () => {
    try {
      const res = await axios.get('http://localhost:3000/api/user-reviews', { withCredentials: true });
      setComments(res.data);
    } catch (err) {
      console.error('Failed to fetch comments:', err);
    }
  };

  const updateProfile = async () => {
    if (!confirmPassword) {
      alert('Please confirm your password to update profile.');
      return;
    }

    try {
      const response = await axios.post('http://localhost:3000/api/updateProfile', {
        ...newProfile,
        password: confirmPassword
      }, { withCredentials: true });

      alert(response.data.message || 'Profile updated successfully!');
      setConfirmPassword('');
    } catch (error) {
      console.error("Error updating profile:", error);
      alert(error.response?.data?.message || 'Failed to update profile.');
    }
  };


  const changePassword = async () => {
    if (!currentPassword || !newPassword) {
      alert('Please fill in both current and new passwords.');
      return;
    }
    try {
      await axios.post('http://localhost:3000/api/changePassword', { currentPassword, newPassword }, { withCredentials: true });
      alert('Password changed successfully!');
      setCurrentPassword('');
      setNewPassword('');
      setShowNotification(true);
    } catch (error) {
      console.error("Error changing password:", error);
      alert('Failed to change password: ' + (error.response?.data?.message || 'Unknown error'));
      setCurrentPassword('');
      setNewPassword('');
    }
  };

  const toggleListing = async (id, enable) => {
    try {
      await axios.post(`http://localhost:3000/api/mylistings/${id}/${enable ? 'enable' : 'disable'}`, {}, {withCredentials: true});
      alert(`Listing ${enable ? 'enabled' : 'disabled'} successfully!`);
      fetchListings();
    } catch (error) {
      console.error("Error toggling listing:", error);
    }
  };

  const removeListing = async (id) => {
    const confirmed = window.confirm("Are you sure you want to delete this listing? This action cannot be undone.");
    if (!confirmed) return;

    try {
      await axios.delete(`http://localhost:3000/api/mylistings/${id}`, { withCredentials: true });
      fetchListings();
    } catch (error) {
      console.error("Error removing listing:", error);
    }
  };

  const handleSignOut = () => {
    axios.post('http://localhost:3000/api/logout', {}, { withCredentials: true })
      .then(() => {
        localStorage.removeItem('cart');
        window.location.href = '/';  // redirect to sign-in
      })
      .catch(error => {
        console.error("Error signing out:", error);
        window.location.href = '/';
      });
  };

  const toggleCommentVisibility = () => {
    setHideComments(!hideComments);
  };

  return (
    <div className="profile-container">
      <h1>Welcome, {user.firstname || 'User'}!</h1>
      <div className="profile-tabs">
        <button onClick={() => setTab('edit')}>Edit Profile</button>
        <button onClick={() => setTab('password')}>Change Password</button>
        <button onClick={() => setTab('listings')}>Manage Listings</button>
        <button onClick={() => setTab('comments')}>View Comments</button>
        <button onClick={() => navigate('/')}>Go to Home</button>
      </div>

      <div className="profile-content">
        {tab === 'edit' && (
          <div className="edit-profile-tab profile-tab-panel">
            <h3>Edit Profile</h3>
            <input value={newProfile.firstname} onChange={e => setNewProfile({ ...newProfile, firstname: e.target.value })} placeholder="First name" />
            <input value={newProfile.lastname} onChange={e => setNewProfile({ ...newProfile, lastname: e.target.value })} placeholder="Last name" />
            <input value={newProfile.email} onChange={e => setNewProfile({ ...newProfile, email: e.target.value })} placeholder="Email address" />
            <div className="password-wrapper">
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="password confirmation"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
              <span className="toggle-password" onClick={() => setShowPassword(!showPassword)}>
                {showPassword ? '🐵' : '🙈'}
              </span>
            </div>
            <button onClick={updateProfile}>Submit</button>
          </div>
        )}

        {tab === 'password' && (
          <div className="change-password-tab profile-tab-panel">
            <h3>Change Password</h3>
            <div className="password-wrapper">
              <input type={showPassword ? 'text' : 'password'} placeholder="Current password" value={currentPassword} onChange={e => setCurrentPassword(e.target.value)} />
              <span className="toggle-password" onClick={() => setShowPassword(!showPassword)}>
                {showPassword ? '🐵' : '🙈'}
              </span>
            </div>
            <div className="password-wrapper">
              <input type={showPassword ? 'text' : 'password'} placeholder="New password" value={newPassword} onChange={e => setNewPassword(e.target.value)} />
              <span className="toggle-password" onClick={() => setShowPassword(!showPassword)}>
                {showPassword ? '🐵' : '🙈'}
              </span>
            </div>
            <button onClick={changePassword}>Submit</button>
            {showNotification && <EmailNotification email={user.email} />}
          </div>
        )}
        

        {tab === 'listings' && (
          <div className="manage-listings-tab profile-tab-panel">
            <h2>These are your items listed {user.firstname || 'User'}</h2>
            <div className="listings-container">
              {listings.filter(item => String(item.seller) === String(user.id)).map(listing => (
                <ListingCard
                  key={listing._id}
                  listing={listing}
                  onEnable={() => toggleListing(listing._id, true)}
                  onDisable={() => toggleListing(listing._id, false)}
                  onRemove={() => removeListing(listing._id)}
                />
              ))}
            </div>
            <div className="listing-actions-group">
              <button className="action-button" onClick={() => navigate('/add-listing')}>Add a new listing</button>
            </div>
          </div>
        )}

        {tab === 'comments' && (
          <div className="view-comments-tab profile-tab-panel">
            <h2>Phone listing comments</h2>
            <div className="toggle-switch">
              <label className="switch">
                <input type="checkbox" checked={hideComments} onChange={toggleCommentVisibility} />
                <span className="slider round"></span>
              </label>
              <span className="toggle-label">
                {hideComments ? 'Comments hidden' : 'Comments shown'}
              </span>
            </div>
            <div className="comments-grid">
              {comments.map(commentGroup => (
                <CommentCard
                  key={commentGroup.listingId}
                  product={{ title: commentGroup.listingTitle, image: commentGroup.image }}
                  comments={hideComments ? commentGroup.comments.filter(c => !c.hidden) : commentGroup.comments}
                />
              ))}
            </div>
          </div>
        )}

        <div className="signout-fixed-footer">
          <button onClick={handleSignOut}>Sign Out</button>
        </div>

      </div>
    </div>
  );
};

export default Profile;
