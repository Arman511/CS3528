document.addEventListener("DOMContentLoaded", function () {
    const userTableBody = document.getElementById("user-table");
    const deleteButtons = document.querySelectorAll(".delete-btn");
    const users = [];

    for (const row of userTableBody.rows) {
        users.push({
            user_id: row.cells[0].innerText.toLowerCase(),
            user_name: row.cells[1].innerText.toLowerCase(),
            user_email: row.cells[2].innerText.toLowerCase(),
        });
    }

    const nameInput = document.getElementById("search-name");
    const emailInput = document.getElementById("search-email");

    const filterUsers = () => {
        const name = nameInput.value.toLowerCase();
        const email = emailInput.value.toLowerCase();

        for (const row of userTableBody.rows) {
            const user = users[row.rowIndex - 1];
            let shouldShow = true;

            if (name && !user.user_name.includes(name))
                shouldShow = false;
            if (email && !user.user_email.includes(email)) {
                shouldShow = false;
            }

            row.style.display = shouldShow ? "" : "none";
        }
    };

    nameInput.addEventListener("input", filterUsers);
    emailInput.addEventListener("input", filterUsers);

    deleteButtons.forEach((deleteButton) => {
        deleteButton.addEventListener("click", async () => {
            const userId = deleteButton.getAttribute("data-id");
            const row = deleteButton.closest("tr");
            const userName = row.cells[1].innerText.trim();

            if (confirm(`Are you sure you want to delete the user "${userName}"?`)) {
                try {
                    const response = await fetch(`/users/delete?uuid=${userId}`, {
                        method: "DELETE",
                    });

                    if (response.ok) {
                        row.remove();
                        users.splice(row.rowIndex - 1, 1);
                    } else {
                        alert("Failed to delete the user.");
                    }
                } catch (error) {
                    console.error("Failed to delete the user:", error);
                    alert("Failed to delete the user.");
                }
            }
        });
    });
});