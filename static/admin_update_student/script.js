document.addEventListener("DOMContentLoaded", () => {
    let attemptedSkills = [];
    const updateForm = document.getElementById("updateForm");
    const errorElement = document.querySelector(".error");
    const successElement = document.querySelector(".success");

    const uuid = document.getElementById("uuid").value;

    updateForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const student_id = document.getElementById("student_id").value;
        const first_name = document.getElementById("first_name").value;
        const last_name = document.getElementById("last_name").value;
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
                `/students/update_student?uuid=${uuid}`,
                {
                    method: "POST",
                    body: formData,
                }
            );

            if (response.ok) {
                window.location.href = "/students/search";
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
