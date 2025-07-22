import axios from 'axios';

export const getUserListings = async (userId) => {
  return axios.get(`http://localhost:3000/api/listings/seller/${userId}`, {
    withCredentials: true
  });
};

export const disableUser = async (userId) => {
  return axios.put(`http://localhost:3000/api/users/${userId}/toggle-disable`, 
    { action: 'deactivate' }, 
    { withCredentials: true }
  );
};

export const activateUser = async (userId) => {
  return axios.put(`http://localhost:3000/api/users/${userId}/toggle-disable`, 
    { action: 'activate' }, 
    { withCredentials: true }
  );
};

export const deleteUser = async (userId) => {
  return axios.delete(`http://localhost:3000/api/users/${userId}`, 
    { withCredentials: true }
  );
}