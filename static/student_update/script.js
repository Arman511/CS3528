const updateForm = document.getElementById("updateForm");
const errorElement = document.querySelector(".error");
const successElement = document.querySelector(".success");
updateForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(updateForm);

    try {
        const response = await fetch(
            `/student/details/${formData.get("student_id")}`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: formData,
            }
        );

        if (response.ok) {
            const student = await response.json();
            console.log("Student updated:", student);
            successElement.textContent = "Student updated successfully";
            successElement.classList.remove("success--hidden");
            errorElement.classList.add("error--hidden");
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
        console.log(newSkill);
        if (newSkill) {
            var select = document.getElementById("skills");
            var option = document.createElement("option");

            if (
                [...select.options].some((option) => option.text === newSkill)
            ) {
                console.log("Skill already exists");
                return;
            }
            const response = await fetch("/skills/attempt_add_skill_student", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    skill_name: newSkill,
                }),
            });
            if (!response.ok) {
                console.error("Error adding skill");
                return;
            }
            const data = response.json();
            option.title = data.skill_description;
            option.value = data._id;
            option.text = newSkill;
            option.selected = true;
            select.appendChild(option);
            document.getElementById("new_skill").value = "";
            console.log("Skill added:", data);
        }
    });
