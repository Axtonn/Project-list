import axios from 'axios';

export const disableListing = async (listingId) => {
    try {
      await axios.put(`http://localhost:3000/api/listings/${listingId}`, 
      { disabled: true }, 
      { withCredentials: true }
    );
      //console.log('Listing disabled:', response.data);
    } catch (error) {
      console.error('Failed to disable listing:', error);
    }
  };

export const activateListing= async (listingId) => {
    try {
      await axios.put(`http://localhost:3000/api/listings/${listingId}`, 
      { disabled: false }, 
      { withCredentials: true }
    );
      //console.log('Listing activated:', response.data);
    } catch (error) {
      console.error('Failed to activate listing:', error);
    }
  };

export const deleteListing  = async (listingId) => {
  try {
    await axios.delete(`http://localhost:3000/api/listings/${listingId}`, {
      withCredentials: true
    });
    //console.log('Listing deleted:', response.data);
  } catch (error) {
    console.error('Failed to delete listing:', error);
  }
};

export const getSellerFullName = async () => {
  try {
    const response = await axios.get(`http://localhost:3000/api/user/full-name`, {
      withCredentials: true
    });
    return response.data.fullname;
  } catch (error) {
    console.error('Failed to fetch user full name:', error);
    return 'Unknown User';
  }
};
export const updateListing = async (listingId, updatedFields) => {
  const response = await axios.put(`http://localhost:3000/api/listings/${listingId}`, updatedFields, {
    withCredentials: true
  });
  return response.data;
};
