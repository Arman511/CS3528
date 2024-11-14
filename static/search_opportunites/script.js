document.addEventListener("DOMContentLoaded", function () {
    const searchForm = document.getElementById("searchForm");
    const opportunityTable = document.getElementById("opportunity-table");
    const errorElement = document.querySelector(".error");

    searchForm.addEventListener("submit", function (event) {
        event.preventDefault();
        const formData = new FormData(searchForm);

        fetch(`/opportunities/search`, {
            method: "GET",
            form: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.error) {
                    errorElement.textContent = data.error;
                    errorElement.classList.remove("error--hidden");
                } else {
                    errorElement.classList.add("error--hidden");
                    renderTable(data);
                }
            })
            .catch((error) => {
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
                <td>${
                    opportunity.company_name ? opportunity.company_name : ""
                }</td>
                <td><a href="${opportunity.url}">${opportunity.url}</a></td>
                <td>${opportunity.location}</td>
                <td>${opportunity.modules_required}</td>
                <td>${opportunity.courses_required}</td>
                <td>${opportunity.spots_available}</td>
                <td>${opportunity.duration}</td>
                <td>
                    <a href="/opportunities/employer_add_update_opportunity?opportunity_id=${
                        opportunity._id
                    }" class="btn btn-info btn-sm">Update</a>
                    <a href="/opportunities/employer_delete_opportunity?opportunity_id=${
                        opportunity._id
                    }" class="btn btn-danger btn-sm">Delete</a>
                </td>
            `;

            opportunityTable.appendChild(row);
        });
    }
});
