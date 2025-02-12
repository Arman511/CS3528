document.addEventListener("DOMContentLoaded", () => {
    let attemptedSkills = [];
    const updateForm = document.getElementById("updateForm");
    const errorElement = document.querySelector(".error");
    const successElement = document.querySelector(".success");
    updateForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const student_id = document.getElementById("student_id").value;
        const student_email = document.getElementById("email").value;
        const selectedCourse = document.getElementById("course").value;
        const skillsSelect = document.getElementById("skills");
        const selectedSkills = [];
        const selecteAttemptedSkills = [];

        Array.from(skillsSelect.options).forEach(option => {
            if (option.selected) {
                if (option.text.includes("(Attempted)")) {
                    selecteAttemptedSkills.push(option.value);
                } else if (attemptedSkills.includes(option.value)) {
                    selecteAttemptedSkills.push(option.value);
                } else {
                    selectedSkills.push(option.value);
                }
            }
        });

        const selectedPlacementDuration = Array.from(document.getElementById("placement_duration").selectedOptions).map(option => option.value);
        const hasCar = document.getElementById("has_car").checked;
        const selectedModules = Array.from(document.getElementById('modules').selectedOptions).map(option => option.value);


        const comments = document.getElementById("comments").value;
        const formData = new FormData();
        formData.append("student_id", student_id);
        formData.append("first_name", first_name);
        formData.append("last_name", last_name);
        formData.append("email", student_email);
        formData.append("course", selectedCourse);
        formData.append("skills", selectedSkills);
        formData.append(
            "placement_duration",
            selectedPlacementDuration
        );
        formData.append("has_car", hasCar);
        formData.append("modules", selectedModules);
        formData.append(
            "attempted_skills",
            selecteAttemptedSkills
        );
        formData.append("comments", comments);

        try {
            const response = await fetch(
                `/students/details/${student_id}`,
                {
                    method: "POST",
                    body: formData,
                }
            );

            if (response.ok) {
                window.location.href = "/students/update_success";
            } else {
                errorElement.textContent = "Error updating student";
                errorElement.classList.remove("error--hidden");
                successElement.classList.add("success--hidden");
            }
        } catch (error) {
            console.error("Error:", error);
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
