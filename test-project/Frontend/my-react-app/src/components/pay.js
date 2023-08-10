import React from "react";
import { PayPalScriptProvider } from "@paypal/react-paypal-js";
import PayPalPayment from "./PayPalPayment";

export default function Paypal() {
    const initialOptions = {
        // Your PayPal client ID
        // Note: Replace this with your actual client ID
        clientId: "Adf1GO83Qh22D-T938DQj9_d7KF-nUTNK5n8bhSkRVZEP1rTDX6mM_BoIxHzreGzuUEhv1ZmkyIN4aPq",
        currency: "USD",
        intent: "capture",
    };

    return (
        <div>
            {/* Wrap the entire component with PayPalScriptProvider */}
            <PayPalScriptProvider options={initialOptions}>
                <h1>Checkout</h1>
                <h2>Pick a payment option</h2>
                <button>Safaricom</button>
                
                {/* Render the PayPalPayment component */}
                <PayPalPayment />
            </PayPalScriptProvider>
        </div>
    );
}
