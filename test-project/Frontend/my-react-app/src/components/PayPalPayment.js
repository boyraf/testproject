import { PayPalButtons } from '@paypal/react-paypal-js';
import React from 'react';

const PayPalPayment = () => {
    // Function to create a PayPal order
    const createOrder = async (data, actions) => {
        try {
            // Fetch shopping cart data from the backend of your application
            const response = await fetch("/get-shopping-cart"); // Replace with the appropriate route
            if (!response.ok) {
                throw new Error('Failed to fetch shopping cart data');
            }
            
            const shoppingCartData = await response.json();

            // Construct the shopping cart array
            const shoppingCart = shoppingCartData.map(item => ({
                id: item.product_id.toString(),
                quantity: item.quantity,
                price: item.price,
            }));

            // Create a PayPal order using the constructed shoppingCart
            const orderResponse = await fetch("/create-paypal-order", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    cart: shoppingCart,
                }),
            });

            if (!orderResponse.ok) {
                throw new Error('Failed to create PayPal order');
            }

            const order = await orderResponse.json();
            return order; // Return the entire order object
        } catch (error) {
            console.error("Error creating PayPal order:", error);
            // Handle the error as required
            throw error; // Rethrow the error to propagate it
        }
    };

    // Function to handle the approval of a PayPal transaction
    const onApprove = async (data, actions) => {
        try {
            const response = await fetch("/capture-paypal-order", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    orderID: data.orderID
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to capture PayPal order');
            }

            const orderData = await response.json();
            const name = orderData.payer.name.given_name;
            alert(`Transaction completed by ${name}`);
        } catch (error) {
            console.error("Error capturing PayPal order:", error);
            // Handle the error as needed
            throw error; // Rethrow the error to propagate it
        }
    };

    return (
        // Render your PayPalPayment component content here, using createOrder and onApprove functions
        // For example, you might use PayPalButton component from the PayPal SDK and pass in these functions

        <PayPalButtons
            createOrder={(data, actions) => createOrder(data, actions)}
            onApprove={(data, actions) => onApprove(data, actions)}
        /> 
    );
};

export default PayPalPayment;
