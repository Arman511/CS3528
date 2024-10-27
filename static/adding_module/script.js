const form = document.querySelector(".module_adding_form");
const errorElement = document.querySelector(".error");

form.addEventListener("submit", function (event) {
    event.preventDefault();

    const formData = new FormData(form);
    const moduleId = formData.get("module_id");
    const moduleName = formData.get("module_name");
    const moduleDescription = formData.get("module_description");

    if (!moduleId || !moduleName || !moduleDescription) {
        errorElement.textContent = "All fields are required.";
        errorElement.classList.remove("error--hidden");
        return;
    }

    errorElement.classList.add("error--hidden");

    fetch("/course_modules/add_module", {
        method: "POST",
        body: formData,
    })
        .then(async (response) => {
            if (response.ok) {
                alert("Module added");
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
