document.addEventListener("DOMContentLoaded", function () {
    const orderModal = document.getElementById("orderModal");
    const closeOrderModal = orderModal.querySelector(".close");

    // Close modal when the close button is clicked
    closeOrderModal.onclick = function () {
        orderModal.style.display = "none";
    };

    // Close modal when clicking outside of it
    window.onclick = function (event) {
        if (event.target === orderModal) {
            orderModal.style.display = "none";
        }
    };

    // Handle "View" button click for Orders
    const orderViewButtons = document.querySelectorAll(".action-btn[data-order-id]");
    orderViewButtons.forEach(button => {
        button.addEventListener("click", function () {
            const orderId = this.getAttribute("data-order-id");

            // Make an AJAX request to fetch order details by ID
            fetch(`/order/${orderId}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error("Network response was not ok");
                    }
                    return response.json();
                })
                .then(data => {
                    console.log("Order Data:", data); // Log the data to check the structure

                    // Check if the response contains an error
                    if (data.error) {
                        alert("Error fetching order details: " + data.error);
                    } else if (data.items && data.items.length > 0) {
                        const orderData = data.items[0]; // Access the first item

                        // Populate the modal with order details
                        const customerName = orderData.user_email || "N/A";
                        const amount = `$${orderData.amount.toFixed(2) || "0.00"}`;
                        const status = orderData.status || "Unknown";

                        console.log("Customer Name:", customerName); // Log for debugging
                        console.log("Amount:", amount); // Log for debugging
                        console.log("Status:", status); // Log for debugging

                        document.getElementById("modalCustomerName").innerText = customerName;
                        document.getElementById("modalAmount").innerText = amount;
                        document.getElementById("modalStatus").innerText = status;

                        // Display the modal
                        orderModal.style.display = "flex"; // Use flex to center the modal
                    } else {
                        alert("No order data found.");
                    }
                })
                .catch(error => {
                    console.error("Error fetching order:", error);
                    alert("An error occurred while fetching the order details.");
                });
        });
    });
});
