import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './AddListing.css';


function AddListing() {
  const [title, setTitle] = useState('');
  const [price, setPrice] = useState('');
  const [quantity, setQuantity] = useState('');
  const [image, setImage] = useState(null);
  const navigate = useNavigate();

  // Brand info
  const [availableBrands, setAvailableBrands] = useState([]);
  const [selectedBrand, setSelectedBrand] = useState('');
  const [customBrand, setCustomBrand] = useState('');
  useEffect(() => {
    const fetchBrands = async () => {
      try {
        const res = await axios.get('http://localhost:3000/api/listings/brands');
        setAvailableBrands([...res.data.brands, 'Other']);
      } catch (err) {
        console.error("Failed to fetch brands:", err);
      }
    };

    fetchBrands();
  }, []);

  const handleSubmit = async () => {
    const errors = [];

    if (!title.trim()) {
      errors.push('Title is required.');
    }
    if (isNaN(Number(price)) || Number(price) < 1) {
      errors.push('Price must be a number greater than or equal to 1.');
    }
    if (Number(price) > 10000) {
      errors.push('Price cannot be more than 10,000.');
    }

    if (Number(quantity) < 1 || isNaN(Number(quantity))) {
      errors.push('Quantity must be a number greater than or equal to 1.');
    }
    if (Number(quantity) > 10000) {
      errors.push('You cannot sell more than 10,000 of one item.');
    }

    if (!selectedBrand || (selectedBrand === 'Other' && !customBrand.trim())) {
      errors.push('Please select or enter a brand.');
    }

    if (errors.length > 0) {
      alert(errors.join('\n'));
      return;
    }

    const formData = new FormData();
    formData.append('title', title);
    formData.append('price', price);
    formData.append('stock', quantity);
    formData.append('image', image);
    const brandToSubmit = selectedBrand === 'Other' ? customBrand : selectedBrand;
    formData.append('brand', brandToSubmit);

    try {
      await axios.post('http://localhost:3000/api/mylistings', formData, {
        withCredentials: true,
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      alert('Listing added successfully!');
      navigate('/profile');
    } catch (err) {
      console.error('Error adding listing:', err);
      alert('Error adding listing');
    }
  };


  return (
    <div className="add-listing-container">
      <h2>Add New Listing</h2>
      <input type="text" placeholder="Item name" onChange={(e) => setTitle(e.target.value)} /><br />
      <input type="number" placeholder="Price" onChange={(e) => setPrice(e.target.value)} /><br />
      <input type="number" placeholder="Quantity" onChange={(e) => setQuantity(e.target.value)} /><br />

      {/* Brand */}
      <select onChange={(e) => setSelectedBrand(e.target.value)} value={selectedBrand}>
        <option value="">Select Brand</option>
        {availableBrands.map((brand, index) => (
          <option key={index} value={brand}>{brand}</option>
        ))}
      </select><br />

      {selectedBrand === 'Other' && (
        <>
          <input
            type="text"
            placeholder="Enter custom brand"
            onChange={(e) => setCustomBrand(e.target.value)}
          /><br />
        </>
      )}

      <input type="file" onChange={(e) => setImage(e.target.files[0])} /><br />
      <button onClick={handleSubmit}>Add Item</button><br /><br />
      <button onClick={() => navigate('/profile')}>Back to Profile</button>
    </div>
  );
}

export default AddListing;
