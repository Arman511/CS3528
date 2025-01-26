document.addEventListener("DOMContentLoaded", function () {
    const searchForm = document.getElementById("searchForm");
    const opportunityTable = document.getElementById("opportunity-table");
    const errorElement = document.querySelector(".error");
    let searchUrl;
    // Fetch the session data to determine the user type
    fetch("/api/session")
    .then((response) => response.json())
    .then((data) => {
        const userType = data.user_type;
        console.log("User Type:", userType);

        // Use userType for your logic
        searchUrl =
            userType === "admin"
                ? "/admin/opportunities/search"
                : "/employer/opportunities/search";

        console.log("Search URL:", searchUrl);
    })
    .catch((error) => console.error("Error fetching session data:", error));


    searchForm.addEventListener("submit", function (event) {
        event.preventDefault();
        const formData = new FormData(searchForm);

        // Convert formData to a JSON object
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });

        // Send the form data as JSON to the dynamic URL
        fetch(searchUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        })
            .then((response) => response.json())
            .then((data) => {
                console.log(data);
                if (data.error) {
                    errorElement.textContent = data.error;
                    errorElement.classList.remove("error--hidden");
                } else {
                    errorElement.classList.add("error--hidden");
                    renderTable(data);
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                errorElement.textContent = "An error occurred while searching.";
                errorElement.classList.remove("error--hidden");
            });
    });

    function renderTable(opportunities) {
        opportunityTable.innerHTML = "";
        opportunities.forEach((opportunity) => {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${opportunity.title}</td>
                <td>${opportunity.description}</td>
                <td>${opportunity.company_name}</td>
                <td><a href="${opportunity.url}">${opportunity.url}</a></td>
                <td>${opportunity.location}</td>
                <td>${opportunity.modules_required}</td>
                <td>${opportunity.courses_required}</td>
                <td>${opportunity.spots_available}</td>
                <td>${opportunity.duration}</td>
                <td>
                    <a href="/opportunities/employer_add_update_opportunity?opportunity_id=${opportunity._id}" class="btn btn-info btn-sm">Update</a>
                    <a href="/opportunities/employer_delete_opportunity?opportunity_id=${opportunity._id}" class="btn btn-danger btn-sm">Delete</a>
                </td>
            `;

            opportunityTable.appendChild(row);
        });
    }
});
