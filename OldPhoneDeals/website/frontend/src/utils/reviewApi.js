import axios from 'axios';

export const disableReview = async (reviewId) => {
    try {
      await axios.patch(`http://localhost:3000/api/review/${reviewId}`, 
      { hidden: true }, 
      { withCredentials: true }
    );
      //console.log('Review disabled:', response.data);
    } catch (error) {
      console.error('Failed to disable Review:', error);
    }
  };

export const activateReview= async (reviewId) => {
    try {
      await axios.patch(`http://localhost:3000/api/review/${reviewId}`, 
      { hidden: false }, 
      { withCredentials: true }
    );
      //console.log('Review activated:', response.data);
    } catch (error) {
      console.error('Failed to activate Review:', error);
    }
  };

export const deleteReview  = async (reviewId) => {
  try {
    await axios.delete(`http://localhost:3000/api/review/${reviewId}`, {
      withCredentials: true
    });
    //console.log('Review deleted:', response.data);
  } catch (error) {
    console.error('Failed to delete Review:', error);
  }
};