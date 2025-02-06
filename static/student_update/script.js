let attemptedSkills = [];
document.addEventListener("DOMContentLoaded", () => {
    let updateForm = document.querySelector(".update_form");
    let errorElement = document.querySelector(".error");
    let successElement = document.querySelector(".success");
    let uuid = document.getElementById("uuid").value;
    updateForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        let student_id = document.getElementById("student_id").value;
        let student_email = document.getElementById("email").value;
        let selectedCourse = document.getElementById("course").value;
        if (selectedCourse === "None") {
            errorElement.textContent = "Please select a course";
            errorElement.classList.remove("error--hidden");
            successElement.classList.add("success--hidden");
            return;
        }
        let selectedSkills = [];
        let selectAttemptedSkills = [];
        let skillsSelect = document.getElementById("skills");
        for (let i = 0; i < skillsSelect.options.length; i++) {
            if (skillsSelect.options[i].selected) {
                if (skillsSelect.options[i].text.includes("(Attempted)")) {
                    selectAttemptedSkills.push(skillsSelect.options[i].value);
                } else if (
                    attemptedSkills.includes(skillsSelect.options[i].value)
                ) {
                    selectAttemptedSkills.push(skillsSelect.options[i].value);
                } else {
                    selectedSkills.push(skillsSelect.options[i].value);
                }
            }
        }
        let selectedPlacementDuration = [];
        let placementDurationSelect =
            document.getElementById("placement_duration");

        for (let i = 0; i < placementDurationSelect.options.length; i++) {
            selectedPlacementDuration.push(
                placementDurationSelect.options[i].value
            );
        }
        let hasCar = document.getElementById("has_car").checked;
        let selectedModules = [];
        let modulesSelect = document.getElementById("modules");
        for (let i = 0; i < modulesSelect.options.length; i++) {
            if (modulesSelect.options[i].selected) {
                selectedModules.push(modulesSelect.options[i].value);
            }
        }
        let comments = document.getElementById("comments").value;
        let formData = new FormData();
        formData.append("student_id", student_id);
        formData.append("email", student_email);
        formData.append("course", selectedCourse);
        formData.append("skills", JSON.stringify(selectedSkills));
        formData.append(
            "placement_duration",
            JSON.stringify(selectedPlacementDuration)
        );
        formData.append("has_car", hasCar);
        formData.append("modules", JSON.stringify(selectedModules));
        formData.append(
            "attempted_skills",
            JSON.stringify(selectAttemptedSkills)
        );
        formData.append("comments", comments);
        try {
            const response = await fetch(`/students/details?uuid=${uuid}`, {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                window.location.href = "/students/update_success";
            } else {
                errorElement.textContent = "Error updating student";
                errorElement.classList.remove("error--hidden");
                successElement.classList.add("success--hidden");
            }
        } catch (error) {
            console.error("Error:", error);
            const errorElement = document.querySelector(".error");
            errorElement.textContent = "Error updating student";
            errorElement.classList.remove("error--hidden");
            successElement.classList.add("success--hidden");
        }
    });

    document
        .getElementById("add_skill")
        .addEventListener("click", async function () {
            var newSkill = document.getElementById("new_skill").value;
            newSkill = newSkill.trim();
            if (newSkill === "") {
                console.log("Skill cannot be empty");
                alert("Skill cannot be empty");
                return;
            }
            if (newSkill) {
                let options = [];
                let selected_skills = document.getElementById("skills");
                Array.from(selected_skills.selectedOptions).map((option) =>
                    options.push(option.text.toLowerCase())
                );
                let unselected_skills = document.querySelectorAll(
                    ".selectize-dropdown-content div"
                );
                for (let i = 0; i < unselected_skills.length; i++) {
                    options.push(unselected_skills[i].innerText.toLowerCase());
                }
                if (
                    options.includes(newSkill.toLowerCase()) ||
                    attemptedSkills.includes(newSkill) ||
                    options.includes(newSkill.toLowerCase() + " (attempted)")
                ) {
                    console.log("Skill already exists");
                    alert("Skill already exists");
                    return;
                }
                let response = await fetch(
                    "/skills/attempt_add_skill_student",
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            skill_name: newSkill,
                        }),
                    }
                );
                if (!response.ok) {
                    console.error("Error adding skill");
                    return;
                }
                let data = await response.json();
                if (attemptedSkills.includes(data._id)) {
                    alert("Skill already exists");
                    return;
                }
                attemptedSkills.push(data._id);

                var $select = $(document.getElementById("skills")).selectize(
                    options
                );
                var selectize = $select[0].selectize;
                selectize.addOption({
                    value: data._id,
                    text: newSkill + " (Attempted)",
                });
                if (selectize.items.length < 10) {
                    selectize.addItem(data._id);
                } else {
                    alert("You cannot add more than 10 skills");
                }
                selectize.refreshOptions();
                document.getElementById("new_skill").value = "";
                alert("Skill added successfully");
            }
        });
});
