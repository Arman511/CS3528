document.addEventListener("DOMContentLoaded", function () {
    const searchForm = document.getElementById("searchForm");
    const employerTableBody = document.getElementById("employer-table");
    const errorElement = document.querySelector(".error");

    // Function to fetch employers
    function fetchEmployers(title = "", email = "") {
        fetch("/employers/search_employers", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title, email }),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Failed to fetch employers");
                }
                return response.json();
            })
            .then((data) => {
                if (data.length === 0) {
                    errorElement.textContent = "No employers found.";
                    errorElement.classList.remove("error--hidden");
                    employerTableBody.innerHTML = "";
                    return;
                }

                errorElement.classList.add("error--hidden");

                // Populate the table
                employerTableBody.innerHTML = data
                    .map(
                        (employer) => `
                        <tr>
                            <td>${employer._id}</td>
                            <td>${employer.company_name}</td>
                            <td>${employer.email}</td>
                            <td>
                                <a href="/employers/update_employer?employer_id=${employer._id}" class="btn btn-info btn-sm mb-2">Update</a>
                                <button class="btn btn-danger btn-sm delete-employer" data-id="${employer._id}">Delete</button>
                            </td>
                        </tr>
                    `
                    )
                    .join("");

                attachDeleteEventListeners();
            })
            .catch((error) => {
                errorElement.textContent =
                    "An error occurred. Please try again.";
                errorElement.classList.remove("error--hidden");
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
                    fetchEmployers(); // Refresh the table dynamically
                }
            })
            .catch((error) => {
                console.error("Error deleting employer:", error);
            });
    }

    // Attach event listeners for delete buttons
    function attachDeleteEventListeners() {
        document.querySelectorAll(".delete-employer").forEach((button) => {
            button.addEventListener("click", function () {
                const employerId = this.dataset.id;
                deleteEmployer(employerId);
            });
        });
    }

    // Fetch all employers on page load
    fetchEmployers();

    // Handle search form submission
    searchForm.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent form submission reload

        // Get form values
        const title = document.getElementById("title").value.trim();
        const email = document.getElementById("email").value.trim();

        // Fetch filtered employers
        fetchEmployers(title, email);
    });
});
