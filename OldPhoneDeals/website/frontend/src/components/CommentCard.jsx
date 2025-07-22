import React, { useState } from 'react';
import './CommentCard.css';

const CommentCard = ({ showNames = false, commentOnly = false, product, comments = [], adminview = false, onHide=()=>{}, onShow=()=>{}, onDelete=()=>{} }) => {
  const [expanded, setExpanded] = useState(false);
  const visibleComments = expanded ? comments : comments.slice(0, 3);

  return (
    <div className="comment-card">
      {!commentOnly &&
        <div className="product-image">
          <img src={product?.image || '/phone-placeholder.png'} alt={product?.title || 'Product'} />
        </div>
      }

      <div className="comments-container">
        {Array.isArray(visibleComments) && visibleComments.length > 0 ? (
          visibleComments.map((c, index) => (
            <div key={index} className="comment-block">
              {showNames && (
                <>
                  {c.reviewer?.lastname ? (
                    <h3 style={{ color: 'black' }}>{c.reviewer.firstname} {c.reviewer.lastname}</h3>
                  ) : (
                    <h3 style={{ color: 'black' }}>Reviewer: Unknown</h3>
                  )}
                </>
              )}
              <p>{c.comment}</p>
              <small>Rating: {c.rating}</small>
              {typeof c.hidden === 'boolean' && (
                <span style={{ color: c.hidden ? 'red' : 'green', marginLeft: '1rem' }}>
                  ({c.hidden ? 'Hidden' : 'Visible'})
                </span>
              )}
              {adminview &&
                <div>
                  {c.hidden ?
                    <button onClick={()=>onShow(c._id)}>
                      Show
                    </button> :
                    <button onClick={()=>onHide(c._id)}>
                      Hide
                    </button>
                  }
                  <button onClick={()=>onDelete(c._id)}>
                    Delete
                  </button>
                </div>
              }
            </div>
          ))
        ) : (
          <p className="no-comments">No comments</p>
        )}

        {comments.length > 3 && (
          <div className="see-more">
            <button onClick={() => setExpanded(!expanded)}>
              {expanded ? 'Show less' : 'See more'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default CommentCard;
