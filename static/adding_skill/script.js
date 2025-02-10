let form = document.querySelector(".skill_adding_form");
let error_paragraph = document.querySelector(".error");
let skill_name_box = document.getElementById("skill_name");
let skill_desc_box = document.getElementById("skill_description");
// Form submission logic
form.addEventListener("submit", function (e) {
    e.preventDefault(); // Prevent form submission
    let formData = new FormData(form); // Collect form data

    fetch("/skills/add_skill", {
        method: "POST",
        body: formData,
    })
        .then(async (response) => {
            if (response.ok) {
                window.location.href = "/skills/search"; // Redirect to the search page
            } else if (response.status === 401 || response.status === 400) {
                let errorResponse = await response.json(); // Parse JSON response
                throw new Error(errorResponse.error); // Throw error with the extracted message
            } else {
                throw new Error("Server error"); // General server error message
            }
        })
        .catch((error) => {
            console.error("Error:", error); // Log error to console
            error_paragraph.textContent = error.message; // Use `error.message` to display the error
            error_paragraph.classList.remove("error--hidden"); // Ensure the error paragraph is visible
        });
});