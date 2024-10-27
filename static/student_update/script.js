let attemptedSkills = [];
document.addEventListener("DOMContentLoaded", () => {
    let updateForm = document.querySelector(".update_form");
    let errorElement = document.querySelector(".error");
    let successElement = document.querySelector(".success");
    updateForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        let student_id = document.getElementById("student_id").value;
        let student_email = document.getElementById("email").value;
        let selectedCourse = document.getElementById("course").value;
        let selectedSkills = [];
        let selecteAttemptedSkills = [];
        let skillsSelect = document.getElementById("skills");
        for (let i = 0; i < skillsSelect.options.length; i++) {
            if (skillsSelect.options[i].selected) {
                if (skillsSelect.options[i].text.includes("(Attempted)")) {
                    selecteAttemptedSkills.push(skillsSelect.options[i].value);
                } else if (
                    attemptedSkills.includes(skillsSelect.options[i].value)
                ) {
                    selecteAttemptedSkills.push(skillsSelect.options[i].value);
                } else {
                    selectedSkills.push(skillsSelect.options[i].value);
                }
            }
        }
        let selectedPlacementDuration = [];
        for (
            let i = 0;
            i < document.getElementsByName("placement_duration").length;
            i++
        ) {
            if (document.getElementsByName("placement_duration")[i].checked) {
                selectedPlacementDuration.push(
                    document.getElementsByName("placement_duration")[i].value
                );
            }
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
            JSON.stringify(selecteAttemptedSkills)
        );
        formData.append("comments", comments);
        try {
            const response = await fetch(
                `/students/details/${formData.get("student_id")}`,
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
            if (newSkill) {
                var select = document.getElementById("skills");
                var option = document.createElement("option");

                if (
                    [...select.options].some(
                        (option) => option.text === newSkill
                    )
                ) {
                    console.log("Skill already exists");
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
                option.value = data._id;
                option.text = newSkill;
                option.selected = true;
                select.appendChild(option);
                document.getElementById("new_skill").value = "";
                attemptedSkills.push(data._id);
                console.log("Skill added:", data);
            }
        });
});
