
document.addEventListener("DOMContentLoaded", function () {
    const skillTableBody = document.getElementById("skill-table");
    const deleteButtons = document.querySelectorAll(".delete-btn");
    const skills = [];

    for (const row of skillsTable.rows) {
        skills.push({
            skill_name: row.cells[0].innerText.toLowerCase(),
            skill_description: row.cells[1].innerText.toLowerCase(),
        });
    }

    const nameInput = document.getElementById("search-skill-name");
    const descriptionInput = document.getElementById("search-skill-description");

    const filterSkills = () => {
        const name = nameInput.value.toLowerCase();

        for (const row of skillTableBody.rows) {
            const skill = skills[row.rowIndex - 1];
            let shouldShow = true;

            if (name && !skill.skill_name.includes(name))
                shouldShow = false;
            if (description && !skill.skill_description.includes(description)) {
                shouldShow = false;
            }

            row.style.display = shouldShow ? "" : "none";
        }
    };

    nameInput.addEventListener("input", filterSkills);

    deleteButtons.forEach((deleteButton) => {
        deleteButton.addEventListener("click", async () => {
            const skillId = deleteButton.getAttribute("data-id");
            const row = deleteButton.closest("tr");
            const skillName = row.cells[0].innerText.trim();

            if (confirm(`Are you sure you want to delete the skill "${skillName}"?`)) {
                try {
                    const response = await fetch(`/skills/delete?skill_id=${skillId}`, {
                        method: "DELETE",
                    });

                    if (response.ok) {
                        row.remove();
                        skills.splice(row.rowIndex - 1, 1);
                    } else {
                        alert("Failed to delete the skill.");
                    }
                } catch (error) {
                    console.error("Failed to delete the skill:", error);
                    alert("Failed to delete the skill.");
                }
            }
        });
    });


});
