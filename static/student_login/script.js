document.addEventListener("DOMContentLoaded", function () {
    let form = document.querySelector(".login_form");
    let error_paragraph = document.querySelector(".error");
    let forgot_password = document.querySelector(".forgot_password");

    // Form submission logic
    form.addEventListener("submit", function (e) {
        e.preventDefault(); // Prevent form submission
        let formData = new FormData(form); // Collect form data

        fetch("/students/login", {
            method: "POST",
            body: formData,
        })
            .then(async (response) => {
                if (response.ok) {
                    window.location.href = `/students/details/${formData.get(
                        "student_id"
                    )}`;
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

    forgot_password.addEventListener("click", function () {
        let student_id = prompt("Enter your student ID");

        if (student_id) {
            fetch(`/students/forgot-password/${student_id})`, {
                method: "POST",
            })
                .then(async (response) => {
                    if (response.ok) {
                        alert("Password reset link sent to your email");
                    } else {
                        let errorResponse = await response.json();
                        throw new Error(errorResponse.error);
                    }
                })
                .catch((error) => {
                    console.error("Error:", error);
                    alert(error.message);
                });
        }
    });
});
