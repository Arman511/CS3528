document.addEventListener("DOMContentLoaded", function () {
    const employerTableBody = document.getElementById("employer-table");
    const errorElement = document.querySelector(".error");
    const titleInput = document.getElementById("title");
    const emailInput = document.getElementById("email");

    // Function to filter table rows based on search criteria
    function filterTableRows() {
        const title = titleInput.value.trim().toLowerCase();
        const email = emailInput.value.trim().toLowerCase();
        const rows = employerTableBody.querySelectorAll("tr");
        let hasResults = false;

        rows.forEach((row) => {
            const companyName = row.children[1].textContent.toLowerCase();
            const employerEmail = row.children[2].textContent.toLowerCase();

            const matchesTitle = title ? companyName.includes(title) : true;
            const matchesEmail = email ? employerEmail.includes(email) : true;

            if (matchesTitle && matchesEmail) {
                row.style.display = ""; // Show row
                hasResults = true;
            } else {
                row.style.display = "none"; // Hide row
            }
        });

        if (!hasResults) {
            errorElement.textContent = "No employers found.";
            errorElement.classList.remove("error--hidden");
        } else {
            errorElement.classList.add("error--hidden");
        }
    }

    // Attach delete functionality to buttons
    function attachDeleteEventListeners() {
        document.querySelectorAll(".delete-employer").forEach((button) => {
            button.addEventListener("click", function () {
                const employerId = this.dataset.id;
                deleteEmployer(employerId);
            });
        });
    }

    // Function to delete an employer
    function deleteEmployer(employerId) {
        if (!confirm("Are you sure you want to delete this employer?")) {
            return;
        }

        fetch("/employers/delete_employer", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ employer_id: employerId }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.error) {
                    alert("Error: " + data.error);
                } else {
                    alert("Employer deleted successfully!");

                    // Remove the corresponding table row
                    const row = document.querySelector(
                        `.delete-employer[data-id="${employerId}"]`
                    ).closest("tr");
                    row.remove();
                }
            })
            .catch((error) => {
                console.error("Error deleting employer:", error);
            });
    }

    // Add event listeners to input fields for live filtering
    titleInput.addEventListener("input", filterTableRows);
    emailInput.addEventListener("input", filterTableRows);

    // Attach delete event listeners on page load
    attachDeleteEventListeners();
});
