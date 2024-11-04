let attemptedSkills = [];
document.addEventListener("DOMContentLoaded", () => {
    const updateForm = document.querySelector(".update_form");
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

        const selectedPlacementDuration = [];
        const placementDurationElements =
            document.getElementsByName("placement_duration");
        for (let i = 0; i < placementDurationElements.length; i++) {
            if (placementDurationElements[i].checked) {
                selectedPlacementDuration.push(
                    placementDurationElements[i].value
                );
            }
        }

        const hasCar = document.getElementById("has_car").checked;
        const selectedModules = [];
        const modulesSelect = document.getElementById("modules");
        for (let i = 0; i < modulesSelect.options.length; i++) {
            if (modulesSelect.options[i].selected) {
                selectedModules.push(modulesSelect.options[i].value);
            }
        }

        const comments = document.getElementById("comments").value;
        const formData = new FormData();
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
                `/students/update/${formData.get("student_id")}`,
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
});
