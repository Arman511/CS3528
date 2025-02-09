
document.addEventListener("DOMContentLoaded", function () {
    const searchForm = document.getElementById("searchForm");
    const skillTableBody = document.getElementById("skill-table");
    const errorElement = document.querySelector(".error");

    // Function to fetch skills
    function fetchSkills(skillName = "") {
        if (!skillName.trim()) {
            errorElement.textContent = "Please enter a skill name to search.";
            errorElement.classList.remove("error--hidden");
            return;
        }
        
        fetch(`/skills/search?query=${encodeURIComponent(skillName)}`, {
            method: "GET",
        })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Failed to fetch skills");
            }
            return response.json();
        })
        .then((data) => {
            if (data.length === 0) {
                errorElement.textContent = "No skills found.";
                errorElement.classList.remove("error--hidden");
                skillTableBody.innerHTML = "";
                return;
            }

            errorElement.classList.add("error--hidden");

            // Populate the table
            skillTableBody.innerHTML = data
                .map(
                    (skill) => `
                    <tr id = "skill-${skill._id}">
                        <td>${skill.skill_name}</td>
                        <td>${skill.skill_description}</td>
                        <td>
                            <button class="btn btn-info btn-sm edit-skill" onclick="editSkill('${skill._id}', '${skill.skill_name}', '${skill.skill_description}')">Edit</button>
                            <button class="btn btn-danger btn-sm delete-skill" onclick="deleteSkill('${skill._id}')">Delete</button>
                        </td>
                    </tr>
                `
                )
                .join("");

            if(skillName) {
                scrollToSkill(skillName);
            }
        })
        .catch((error) => {
            console.error("Error fetching skills:", error)
            errorElement.textContent = "An error occurred. Please try again.";
            errorElement.classList.remove("error--hidden");
        });
    }

    function scrollToSkill(query){
        const rows = document.querySelectorAll("#skill-table tr");
        let found = false;

        rows.forEach(row => {
            const skillName = row.cells[0].textContent.toLowerCase();
            if (skillName.includes(query.toLowerCase())) {
                row.scrollIntoView({ behavior: "smooth", block: "center" }); // Scroll to skill
                row.classList.add("highlight"); // Apply the CSS highlight effect
                found = true;
    
                // Remove highlight after 2 seconds
                setTimeout(() => row.classList.remove("highlight"), 2000);
            }
        });

        if (!found) {
            alert("Skill not found!");
        }
    }

    // Function to delete a skill
    window.deleteSkill = function (skillId) {
        if (!confirm("Are you sure you want to delete this skill?")) return;

        fetch("/skills/delete", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: `skill_id=${skillId}`,
        })
        .then((response) => response.json())
        .then((data) => {
            if (data.message) {
                alert("Skill deleted successfully!");
                fetchSkills(); // Refresh the table
            } else {
                alert("Error: " + data.error);
            }
        })
        .catch((error) => {
            console.error("Error deleting skill:", error);
        });
    };

    // Function to edit a skill
    window.editSkill = function (skillId, skillName, skillDescription) {
        const newName = prompt("Enter new skill name:", skillName);
        const newDescription = prompt("Enter new description:", skillDescription);

        if (!newName || !newDescription) return;

        fetch("/skills/update", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: `skill_id=${skillId}&skill_name=${newName}&skill_description=${newDescription}`,
        })
        .then((response) => response.json())
        .then((data) => {
            if (data.message) {
                window.location.reload();
            } else {
                alert("Error: " + data.error);
            }
        });
    };

    // Fetch all skills on page load
    fetchSkills();

    // Handle search form submission
    searchForm.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent page reload
        const skillName = document.getElementById("search-skill").value.trim();
        fetchSkills(skillName);
    });
});
