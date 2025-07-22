export const filterAndSortListings = (listings, searchTerm, sortKey, sortOrder = 'asc') => {
  let filtered = listings.filter((listing) =>
    listing.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    listing.brand.toLowerCase().includes(searchTerm.toLowerCase())
  );

  filtered.sort((a, b) => {
    let valA = a[sortKey];
    let valB = b[sortKey];

    if (typeof valA === 'string') valA = valA.toLowerCase();
    if (typeof valB === 'string') valB = valB.toLowerCase();

    if (sortOrder === 'asc') {
      return valA > valB ? 1 : -1;
    } else {
      return valA < valB ? 1 : -1;
    }
  });

  return filtered;
};

export const filterAndSortUsers = (users, searchTerm, sortKey, sortOrder = 'asc') => {
  let filtered = users.filter((user) =>
    user.firstname.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.lastname.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  filtered.sort((a, b) => {
    let valA = a[sortKey];
    let valB = b[sortKey];

    if (valA instanceof Date) valA = valA.getTime();
    if (valB instanceof Date) valB = valB.getTime();

    if (typeof valA === 'string') valA = valA.toLowerCase();
    if (typeof valB === 'string') valB = valB.toLowerCase();

    if (sortOrder === 'asc') {
      return valA > valB ? 1 : -1;
    } else {
      return valA < valB ? 1 : -1;
    }
  });

  return filtered;
};

export const filterAndSortComments = (comments, searchTerm, sortKey, sortOrder = 'asc') => {
  const lowerSearch = searchTerm.toLowerCase();

  if (sortKey === 'comment') {
    
  }
  let filtered = comments.filter(comment => {
    const commentText = comment.comment?.toLowerCase() || '';
    const reviewerName = `${comment.reviewer?.firstname || ''} ${comment.reviewer?.lastname || ''}`.toLowerCase();
    const ratingText = String(comment.rating || '').toLowerCase(); // convert number to string to match search
    const hiddenText = comment.hidden ? 'hidden' : 'visible'; 
    // map boolean to text
    if (sortKey === 'comment') {
      return commentText.includes(lowerSearch);
    } else if (sortKey === 'reviewer') {
      return reviewerName.includes(lowerSearch);
    } else if (sortKey === 'rating') {
      return ratingText.includes(lowerSearch);
    } else if (sortKey === 'hidden') {
      return hiddenText.includes(lowerSearch);
    } else {
      return true; // default to showing all if sortKey isn't recognized
    }
  });
  //raiting, reviewert
  filtered.sort((a, b) => {
    let valA, valB;

    if (sortKey === 'reviewerName') {
      valA = `${a.reviewer?.firstname || ''} ${a.reviewer?.lastname || ''}`.toLowerCase();
      valB = `${b.reviewer?.firstname || ''} ${b.reviewer?.lastname || ''}`.toLowerCase();
    } else {
      valA = a[sortKey];
      valB = b[sortKey];
      if (typeof valA === 'string') valA = valA.toLowerCase();
      if (typeof valB === 'string') valB = valB.toLowerCase();
    }

    if (sortOrder === 'asc') {
      return valA > valB ? 1 : -1;
    } else {
      return valA < valB ? 1 : -1;
    }
  });

  return filtered;
};
