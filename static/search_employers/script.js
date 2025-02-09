document.addEventListener("DOMContentLoaded", function () {
    const employerTableBody = document.getElementById("employer-table");
    const errorElement = document.querySelector(".error");
    const titleInput = document.getElementById("title");
    const emailInput = document.getElementById("email");
    const deleteButtons = document.querySelectorAll(".delete-employer");
    const employers = [];

    for (row of employerTableBody.rows) {
        employers.push({
            id: row.cells[0].textContent,
            title: row.cells[1].textContent,
            email: row.cells[2].textContent,
        });
    }

    // Function to filter table rows based on search criteria
    function filterTableRows() {
        const title = titleInput.value.trim().toLowerCase();
        const email = emailInput.value.trim().toLowerCase();
        const rows = employerTableBody.querySelectorAll("tr");
        let hasResults = false;

        for (const row of employerTableBody.rows) {
            const employer = employers[row.rowIndex - 1];
            let shouldShow = true;

            if (title && !employer.title.toLowerCase().includes(title)) shouldShow = false;
            if (email && !employer.email.toLowerCase().includes(email)) shouldShow = false;

            row.style.display = shouldShow ? "" : "none";

        }
    }

    // Add event listeners to input fields for live filtering
    titleInput.addEventListener("input", filterTableRows);
    emailInput.addEventListener("input", filterTableRows);

    deleteButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const employerId = button.dataset.id;
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
        });
    });
});
