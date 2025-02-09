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
        let form = new FormData();
        form.append("skill_id", skillId);
        form.append("skill_name", skillName);
        form.append("skill_description", skillDescription);

        fetch("/skills/update", {
            method: "POST",
            body: form
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    errorElement.textContent = data.error;
                    errorElement.classList.remove("error--hidden");
                } else {
                    window.location.href = "/skills/search";
                }
            })
            .catch(error => {
                console.error("Error:", error);
                errorElement.textContent = "An error occurred while updating the skill.";
                errorElement.classList.remove("error--hidden");
            });
    });
});