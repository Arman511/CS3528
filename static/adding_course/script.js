const form = document.querySelector(".course_adding_form");
const errorElement = document.querySelector(".error");

form.addEventListener("submit", function (event) {
    event.preventDefault();

    const formData = new FormData(form);
    const courseId = formData.get("course_id");
    const courseName = formData.get("course_name");
    const courseDescription = formData.get("course_description");

    if (!courseId || !courseName || !courseDescription) {
        errorElement.textContent = "All fields are required.";
        errorElement.classList.remove("error--hidden");
        return;
    }

    errorElement.classList.add("error--hidden");

    fetch("/courses/add_course", {
        method: "POST",
        body: formData,
    })
        .then(async (response) => {
            if (response.ok) {
                alert("Course added");
                form.reset();
            } else if (response.status === 401 || response.status === 400) {
                const errorResponse = await response.json();
                throw new Error(errorResponse.error);
            } else {
                throw new Error("Server error");
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            errorElement.textContent = error.message;
            errorElement.classList.remove("error--hidden");
        });
});
