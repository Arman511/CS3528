document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".skill_adding_form");
    const errorElement = document.querySelector(".error");
    const skillIdElement = document.getElementById("_id");

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        const skillId = skillIdElement.getAttribute("data-id");
        const skillName = document.getElementById("skill_name").value;
        const skillDescription = document.getElementById("skill_description").value;

        if (!skillName || !skillDescription) {
            errorElement.textContent = "One of the inputs is blank";
            errorElement.classList.remove("error--hidden");
            return;
        }

        fetch("/skills/update_attempted_skill", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                skill_id: skillId,
                skill_name: skillName,
                skill_description: skillDescription
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    errorElement.textContent = data.error;
                    errorElement.classList.remove("error--hidden");
                } else {
                    window.location.href = "/skills/attempted_skill_search";
                }
            })
            .catch(error => {
                console.error("Error:", error);
                errorElement.textContent = "An error occurred while updating the skill.";
                errorElement.classList.remove("error--hidden");
            });
    });
});