import { useState, useEffect } from 'react'
import React from 'react';
import { useNavigate } from 'react-router-dom';

import './Checkout.css'

import axios from 'axios';
import FileSaver from 'file-saver'; // For exporting sales logs

function Checkout() {
    const navigate = useNavigate();
    const [listings, setListings] = useState([]); // Currently using this as temporary cart

    // Takes entire listings array and adds up the total cost
    const totalPrice = listings.reduce((sum, item) => {
        const quantity = item.quantity;
        return sum + quantity * item.price;
    }, 0);

    // Function that removes item from cart based off id
    const handleDelete = (listingToDelete) => {
        const updatedListings = listings.filter(listing => listing._id !== listingToDelete._id); // Finding item to delete
        setListings(updatedListings);
        localStorage.setItem("cart", JSON.stringify(updatedListings)); // Updating cart local storage
    }

    const handleQuantityChange = (listing, event) => { // Called when user changes value in quantity
        let value = parseInt(event.target.value, 10); // Store new value

        // Cap the value at the stock quantity
        if (value > listing.stock) value = listing.stock;
    
        if (value === 0) { // If new quantity is 0, remove item
            handleDelete(listing);
        } else { // Copies existing state and updates change value
            const updatedListings = listings.map(item =>
                item._id === listing._id ? { ...item, quantity: value } : item
            );

            setListings(updatedListings);
            localStorage.setItem("cart", JSON.stringify(updatedListings));
            }
    };

    // Called when checkout button is pressed
    const handleCheckout = async () => {
        // Checking that checkout is not empty
        if (listings.length ===0 ) {
            alert("You have nothing to checkout. Your cart is empty");
            return;
        }

        try {
            // Getting current user logged in data
            const userResponse = await axios.get('http://localhost:3000/api/user/user-info', {
                withCredentials: true
            });
            const firstname = userResponse.data.firstname;
            const lastname = userResponse.data.lastname;
            const buyerName = `${firstname} ${lastname}`; // Setting buyername

            // Create array of objects storing data required to make sales log
            const salesData = {
                items: listings.map(listing => ({
                    _id: listing._id, // Sending id so we can update stock quantities
                    item: listing.title,
                    price: listing.price,
                    quantity: listing.quantity,
                })),
                buyerName: buyerName
            };
            // Send salesData to backend
            const response = await axios.post("http://localhost:3000/api/checkout", salesData);
    
            if (response.status === 201) {
                alert('Checkout successful!');
                // Reset the cart after successful checkout
                setListings([]);
                localStorage.removeItem('cart');
                navigate('/') // Back to home page
            } else {
                alert(`Error: ${response.data.error}`);
            }
        } catch (error) {
            console.error("Error during checkout:", error.response?.data || error.message);
            alert('Failed to complete checkout.');
        }
    };

    // When we enter checkout page, we getting cart info and saving to state array
    useEffect(() => {
        const savedCart = localStorage.getItem("cart"); // Get the saved cart from Local Storage
        if (savedCart && savedCart !== "null" && savedCart !== "undefined") {
            const parsedCart = JSON.parse(savedCart);
            setListings(parsedCart); // Temporary cus everything is using listings array
        }
    }, [])

    return (
        <>
            <div className="checkout-container">
                <h1>Checkout Page</h1>
                <table className="checkout-table">
                    <thead>
                        <tr>
                        <th>Item</th>
                        <th>Quantity</th>
                        <th>Price</th>
                        <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {listings.map(listing => (
                            <tr key={listing._id}>
                                <td>{listing.title}</td>{/* TITLE */}
                                <td>{/* QUANTITY */}
                                    <input 
                                        type="number" 
                                        value={listing.quantity}
                                        min="0"
                                        max={listing.stock}
                                        onChange={(e) => handleQuantityChange(listing, e)}
                                    />
                                </td>
                                <td>${listing.price.toFixed(2)}</td>{/* PRICE */}
                                <td>{/* DELETE BUTTON */}
                                <button onClick={() => handleDelete(listing)}> 
                                    <img src="src/assets/red_bin.png" alt="button icon" style={{ width: '20px', height: '20px' }} />
                                </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                <h2>Total: ${totalPrice.toFixed(2)}</h2>{/* TOTAL PRICE */}
                <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center',
                    alignItems: 'center', 
                }}>
                {/* Checkout Button */}
                <button style={{ display: 'block' }} onClick={handleCheckout}> CHECKOUT </button>
                <button style={{ display: 'block' }} onClick={() => navigate('/')}>HOME</button>
                <button style={{ display: 'block' }} onClick={() => navigate(-1)}>BACK</button>
                </div>
            </div>
        </>
    );
}

export default Checkout;