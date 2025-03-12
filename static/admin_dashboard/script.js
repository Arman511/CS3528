document.addEventListener("DOMContentLoaded", function () {
    function fetchDeadlineData() {
        fetch("/user/home", {
            headers: { "Accept": "application/json" },
        })
            .then(response => response.json())
            .then(data => {
                updateDeadlineUI(data);
            })
            .catch(error => console.error("Error fetching deadline data:", error));
    }

    function updateDeadlineUI(data) {
        // Update Deadline Tracker
        document.getElementById("deadline-name").textContent = data.deadline_name;
        document.getElementById("deadline-date").textContent = data.deadline_date || "🎉";

        // Update Stats Card
        let statsCard = document.getElementById("stats-card");
        statsCard.innerHTML = ""; // Clear previous content

        if (data.deadline_name.includes("Add Details")) {
            statsCard.innerHTML = `
                <h5>Students Completed</h5><p class="display-4">${data.num_students}</p>
                <h5>Opportunities Added</h5><p class="display-4">${data.num_opportunities}</p>
            `;

        } else if (data.deadline_name.includes("Students Ranking")) {
            statsCard.innerHTML = `
                <div style="text-align: center;">
                    <h5>Students Ranked</h5>
                    <p class="display-4">${data.num_students}</p>
                </div>
            `;
        } else if (data.deadline_name.includes("Employers Ranking")) {
            statsCard.innerHTML = `
                <div style="text-align: center;">
                    <h5>Employers Ranked</h5>
                    <p class="display-4">${data.num_opportunities}</p>
                </div>
            `;
        }
    }

    fetchDeadlineData(); // Initial load
});
