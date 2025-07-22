import { useState } from 'react';
import { filterAndSortComments } from '../utils/filterAndSort';
import CommentCard from './CommentCard';
import { activateReview, disableReview, deleteReview } from '../utils/reviewApi';
import './AdminCommentList.css';

const AdminCommentList = ({ comments, refreshView }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortKey, setSortKey] = useState('comment');
  const [sortOrder, setSortOrder] = useState('asc');
  // one function to handle all imported review actions
  const handleReviewAction = async (actionFunction, reviewId) => {
    try {
      await actionFunction(reviewId);
      await refreshView();
    } catch (error) {
      console.error('Failed to perform review action:', error);
    }
  };

  const filteredComments = filterAndSortComments(comments, searchTerm, sortKey, sortOrder);

  return (
    <div className='comment-container'>
      <input
        type="text"
        placeholder="Search by comment or reviewer"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />

      <select onChange={(e) => setSortKey(e.target.value)} value={sortKey}>
        <option value="comment">Comment</option>
        <option value="rating">Rating</option>
        <option value="reviewer">Reviewer Name</option>
        <option value="hidden">Is hidden</option>
      </select>

      <select onChange={(e) => setSortOrder(e.target.value)} value={sortOrder}>
        <option value="asc">Asc</option>
        <option value="desc">Desc</option>
      </select>

      <CommentCard
        showNames={true}
        comments={filteredComments}
        commentOnly={true}
        adminview={true}
        reviewerName={true}
        onDelete={(reviewId) => handleReviewAction(deleteReview, reviewId)}
        onShow={(reviewId) => handleReviewAction(activateReview, reviewId)}
        onHide={(reviewId) => handleReviewAction(disableReview, reviewId)}
        className='comment-card'
      />
    </div>
  );
};


export default AdminCommentList