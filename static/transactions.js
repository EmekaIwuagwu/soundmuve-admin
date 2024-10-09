document.addEventListener("DOMContentLoaded", function () {
    const transactionModal = document.getElementById("transactionModal");
    const closeTransactionModal = transactionModal.querySelector(".close");

    // Close modal when the close button is clicked
    closeTransactionModal.onclick = function () {
        transactionModal.style.display = "none";
    };

    // Close modal when clicking outside of it
    window.onclick = function (event) {
        if (event.target === transactionModal) {
            transactionModal.style.display = "none";
        }
    };

    // Handle "View" button click for Transactions
    const transactionViewButtons = document.querySelectorAll(".action-btn[data-transaction-id]");
    transactionViewButtons.forEach(button => {
        button.addEventListener("click", function () {
            const transactionId = this.getAttribute("data-transaction-id");
            const transactionStatus = this.getAttribute("data-status");
            fetch(`/transaction/${transactionId}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.error) {
                        alert(data.error);
                        return;
                    }

                    // Populate modal with data
                    document.getElementById("modalUserName").textContent = data.user_name;
                    document.getElementById("modalAmount").textContent = data.amount;
                    document.getElementById("modalStatus").textContent = data.status;
                    document.getElementById("modalNarration").textContent = data.narration;

                    // Show or hide action form based on transaction status
                    const actionContainer = document.getElementById("actionContainer");
                    const transactionForm = document.getElementById("transactionForm");

                    if (data.status === "Pending") {
                        actionContainer.style.display = "block"; // Show the form
                    } else {
                        actionContainer.style.display = "none"; // Hide the form
                    }

                    // Show the modal
                    transactionModal.style.display = "block";
                })
                .catch(error => {
                    console.error("Error fetching transaction data:", error);
                });
        });
    });
});
