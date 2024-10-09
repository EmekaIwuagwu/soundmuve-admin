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
            fetch(`/order/${orderId}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok ' + response.statusText);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.error) {
                        alert(data.error);
                        return;
                    }
                    // Populate modal with data
                    document.getElementById("modalCustomerName").textContent = data.customer_name;
                    document.getElementById("modalAmount").textContent = data.amount;
                    document.getElementById("modalStatus").textContent = data.status;

                    const itemsList = document.getElementById("modalItems");
                    itemsList.innerHTML = ""; // Clear previous items
                    data.items.forEach(item => {
                        const listItem = document.createElement("li");
                        listItem.textContent = `${item.name} - $${item.price}`;
                        itemsList.appendChild(listItem);
                    });

                    // Show the modal
                    orderModal.style.display = "block";
                })
                .catch(error => {
                    console.error("Error fetching order data:", error);
                });
        });
    });
});
