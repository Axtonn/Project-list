import { useState, useEffect } from 'react';
import axios from 'axios';
import UserList from '../components/AdminUserList';
import ListingList from '../components/AdminListingList'
import AdminListingLog from '../components/AdminListingLog';
import CommentList from '../components/AdminCommentList';
import useIdleLogout from '../utils/useIdleLogout';
import { useNavigate } from 'react-router-dom';
import FileSaver from 'file-saver'; // For exporting sales logs
import './AdminView.css'

const AdminView = () => {
  const [userList, setUserList] = useState([]);
  const [listingList, setListingList] = useState([]);
  const [commentList, setCommentList] = useState([]);
  const [adminDisplay, setAdminDisplay] = useState('users');
  const navigate = useNavigate();
  const secondsLeft = useIdleLogout();
  const getUsers = async () => {
    try {
      const response = await axios.get('http://localhost:3000/api/full-user-info', {
        withCredentials: true
      });
      setUserList(response.data);

      //console.log('Users fetched', response.data);
    } catch (error) {
      console.error('Failed to fetch users:', error);
    }
  };

  const getListings = async () => {
    try {
      const response = await axios.get('http://localhost:3000/api/listings', {}, {
        withCredentials: true
      });
      setListingList(response.data);
    } catch (error) {
      console.error('Failed to fetch listings:', error);
    }
  };

  const getComments = async () => {
    try {
      // console.log('calling')
      const response = await axios.get('http://localhost:3000/api/comments', {
        withCredentials: true
      });
      // console.log(response.data)
      setCommentList(response.data);
    } catch (error) {
      console.error('Failed to fetch comments:', error);
    }
  }

  const logout = async () => {
    try {
      await axios.post('http://localhost:3000/api/logout', {}, {
        withCredentials: true
      });
      localStorage.clear(); // clear any stored session
      window.location.href = '/auth'; // force full page reload (kills any React state/timers)
    } catch (error) {
      console.error('Error during logout:', error);
    }
  };

  // Exports sales logs into JSON format
  const exportSales = async () => {
    try {
      const response = await axios.get(`http://localhost:3000/api/export-sales`, {
        responseType: 'blob'
      });
      // Create a Blob from the response data and trigger the download
      const blob = new Blob([response.data], { type: 'application/json' });
      FileSaver.saveAs(blob, 'sales_export.json'); // File download
    } catch (err) {
      console.error('Failed to export sales:', err);
      alert('Failed to export sales data.');
    }
  };

  // check if user entered admin view is indeed an admin
  useEffect(() => {
    const checkUserRole = async () => {
      try {
        const response = await axios.get('http://localhost:3000/api/user-info', {
          withCredentials: true
        });
        if (response.data.role !== 'admin') {
          alert('Access denied. Admin only.');
          //navigate('/');
          return false;
        }
        return true;

      } catch (error) {
        console.error('Role check failed:', error);
        alert('Please log in.');
        //navigate('/');
        return false;
      }
    }

    const updateAdminView = async () => {
      await getUsers();
      await getListings();
      await getComments();
    };
    if (checkUserRole()) {
      updateAdminView();
    }
  }, []);

  // displays four admin actions in one page

  return (
    <div className='adminview-container'>
      <nav className='nav-style'>
        <div>
          <p style={{ textAlign: 'center', fontStyle: 'italic' }}>
            ⏳ Auto logout in: {secondsLeft}s
          </p>
          <button onClick={() => setAdminDisplay('users')}>Users</button>
          <button onClick={() => setAdminDisplay('listings')}>Listings</button>
          <button onClick={() => setAdminDisplay('comments')}>Comments</button>
          <button onClick={() => setAdminDisplay('inputLogs')}>Listing Logs</button>
          <button onClick={exportSales}> EXPORT SALES (JSON) </button>
        </div>
        <div>
          <button onClick={logout}>Logout</button>
        </div>
      </nav>

      {
        adminDisplay === 'users'
          ? (<UserList users={userList} refreshUserView={getUsers} refreshListingView={getListings} />)
          : (adminDisplay === 'listings')
            ? (<ListingList listings={listingList} refreshView={getListings} />)
            : (adminDisplay === 'comments')
              ? (<CommentList comments={commentList} refreshView={getComments} />)
              : (adminDisplay === 'inputLogs')
                ? (<AdminListingLog />)
                : " "
      }

    </div>
  );
};

export default AdminView;
