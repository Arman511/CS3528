document.addEventListener("DOMContentLoaded", function () {
    fetch("/user/home", {
        headers: { "X-Requested-With": "XMLHttpRequest" }  // Ensures JSON response
    })
    .then(response => response.json())
    .then(data => {
        console.log("Fetched Data:", data);

        const deadlineContainer = document.getElementById("deadline-container");
        deadlineContainer.innerHTML = ""; // Clear existing content

        if (data.deadline_date) {
            deadlineContainer.innerHTML = `
                <div class="alert alert-info text-center" role="alert">
                    <p class="lead mb-0"><strong>${data.deadline_name}</strong></p>
                    <p class="display-4 mt-2 mb-0">${data.deadline_date}</p>
                </div>
            `;
        } else {
            deadlineContainer.innerHTML = `
                <div class="alert alert-success text-center" role="alert">
                    <p class="lead mb-0">No upcoming deadlines</p>
                    <p class="display-4 mt-2 mb-0">🎉</p>
                </div>
            `;
        }
    })
    .catch(error => {
        console.error("Error fetching deadlines:", error);
        document.getElementById("deadline-container").innerHTML = `
            <div class="alert alert-danger text-center" role="alert">
                <p class="lead mb-0">Error loading deadlines.</p>
            </div>
        `;
    });
});
