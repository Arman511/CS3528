document.addEventListener('DOMContentLoaded', function () {
    const searchForm = document.getElementById("searchForm");
    const skillsTable = document.getElementById("attempted-skills-table");
    const approveButtons = document.querySelectorAll(".approve-btn");
    const updateButtons = document.querySelectorAll(".update-btn");
    const rejectButtons = document.querySelectorAll(".reject-btn");
    const skills = [];

    for (const row of skillsTable.rows) {
        skills.push({
            skill_name: row.cells[0].innerText.toLowerCase(),
            skill_description: row.cells[1].innerText.toLowerCase(),
            used: parseInt(row.cells[2].innerText, 10),
        });
    }

    const nameInput = document.getElementById("name");
    const descriptionInput = document.getElementById("description");
    const usageMinInput = document.getElementById("usage_min");
    const usageMaxInput = document.getElementById("usage_max");

    const filterSkills = () => {
        const filters = {
            name: nameInput.value.toLowerCase(),
            description: descriptionInput.value.toLowerCase(),
            usage_min: parseInt(usageMinInput.value, 10),
            usage_max: parseInt(usageMaxInput.value, 10),
        };

        for (const row of skillsTable.rows) {
            const skill = skills[row.rowIndex - 1];
            let shouldShow = true;

            if (filters.name && !skill.skill_name.includes(filters.name))
                shouldShow = false;
            if (filters.description && !skill.skill_description.includes(filters.description))
                shouldShow = false;
            if (!isNaN(filters.usage_min) && skill.used < filters.usage_min)
                shouldShow = false;
            if (!isNaN(filters.usage_max) && skill.used > filters.usage_max)
                shouldShow = false;

            row.style.display = shouldShow ? "" : "none";
        }
    };

    nameInput.addEventListener("input", filterSkills);
    descriptionInput.addEventListener("input", filterSkills);
    usageMinInput.addEventListener("input", filterSkills);
    usageMaxInput.addEventListener("input", filterSkills);

    for (const approveButton of approveButtons) {
        approveButton.addEventListener("click", async () => {
            const skillId = approveButton.getAttribute("data-id");
            const row = approveButton.closest("tr");
            const descriptionCell = row.cells[1];
            let description = descriptionCell.innerText.trim();

            if (!description) {
                description = prompt("Please enter a description for this skill:");
                if (!description) {
                    alert("Description is required to approve the skill.");
                    return;
                }
                descriptionCell.innerText = description;
            }

            const response = await fetch(`/skills/approve_skill?attempt_skill_id=${skillId}`, {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ description })
            });

            if (response.ok) {
                window.location.reload();
            } else {
                alert("Failed to approve the skill.");
            }
        });
    }


    for (const updateButton of updateButtons) {
        updateButton.addEventListener("click", async () => {
            const skillId = updateButton.getAttribute("data-id");
            window.location.href = `/skills/update_attempted_skill?attempt_skill_id=${skillId}`;
        });
    }

    for (const rejectButton of rejectButtons) {
        rejectButton.addEventListener("click", async () => {
            const skillId = rejectButton.getAttribute("data-id");
            if (confirm("Are you sure you want to reject this skill?")) {
                const response = await fetch(`/skills/reject_skill?attempt_skill_id=${skillId}`, { method: "POST" });
                if (response.ok) {
                    window.location.reload();
                } else {
                    alert("Failed to reject the skill.");
                }
            }
        });
    }
});
