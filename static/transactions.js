document.addEventListener("DOMContentLoaded", function () {
    const transactionModal = document.getElementById("transactionModal");
    const closeTransactionModal = transactionModal.querySelector(".close");

    // Close modal when the close button is clicked
    closeTransactionModal.onclick = function () {
        transactionModal.style.display = "none"; // Hide modal
    };

    // Handle "View" button click for Transactions
    const transactionViewButtons = document.querySelectorAll(".action-btn[data-transaction-id]");
    transactionViewButtons.forEach(button => {
        button.addEventListener("click", function () {
            const transactionId = this.getAttribute("data-transaction-id");
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
                    document.getElementById("modalUserName").textContent = data.userName;
                    document.getElementById("modalAmount").textContent = data.amount;
                    document.getElementById("modalStatus").textContent = data.status;
                    document.getElementById("modalNarration").textContent = data.narration;

                    // Show or hide action form based on transaction status
                    const actionContainer = document.getElementById("actionContainer");
                    const transactionForm = document.getElementById("transactionForm");

                    if (data.status === "Pending") {
                        actionContainer.style.display = "block"; // Show action container
                        transactionForm.style.display = "block"; // Show form
                    } else {
                        actionContainer.style.display = "none"; // Hide action container
                        transactionForm.style.display = "none"; // Ensure form is hidden
                    }

                    // Set the transaction ID on the modal for later use
                    transactionModal.setAttribute("data-transaction-id", transactionId);

                    // Show the modal
                    $(transactionModal).modal('show'); // Use Bootstrap's modal function
                })
                .catch(error => {
                    console.error("Error fetching transaction data:", error);
                });
        });
    });

    // Handle the form submission for approval or decline
    const transactionForm = document.getElementById("transactionForm");
    transactionForm.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent the default form submission

        const selectedAction = document.querySelector('input[name="action"]:checked').value;
        const transactionId = transactionModal.getAttribute("data-transaction-id"); // Get the transaction ID

        // Send the selected action to the server
        fetch(`/transaction/${transactionId}/update`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ action: selectedAction }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                alert("Transaction status updated successfully!");
                $(transactionModal).modal('hide'); // Close the modal using Bootstrap's modal function
                // Optionally, refresh the page or update the UI to reflect the changes
                location.reload(); // Reload the page to see the changes
            } else {
                alert(data.error);
            }
        })
        .catch(error => {
            console.error("Error updating transaction status:", error);
        });
    });
});
