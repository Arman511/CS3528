document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector(".change_password");
    const errorParagraph = document.querySelector(".error");

    form.addEventListener("submit", function (e) {
        e.preventDefault(); // Prevent form submission for validation

        // Grab form field values
        const email = form.email.value;
        const oldPassword = form.old_password.value;
        const newPassword = form.new_password.value;
        const confirmPassword = form.confirm_password.value;

        // Clear previous errors
        errorParagraph.classList.add("error--hidden");

        // Check if new password and old password are the same
        if (oldPassword === newPassword) {
            errorParagraph.textContent = "The new password cannot be the same as the old password.";
            errorParagraph.classList.remove("error--hidden");
            return;
        }

        // Check if new password and confirm password match
        if (newPassword !== confirmPassword) {
            errorParagraph.textContent = "New password and confirm password do not match.";
            errorParagraph.classList.remove("error--hidden");
            return;
        }

        // If all validations pass, submit the form
        let formData = new FormData(form);

        fetch("/user/change_password", {
            method: "POST",
            body: formData,
        })
            .then(async (response) => {
                if (response.ok) {
                    window.location.href = "/"; // Redirect on success
                } else {
                    let errorResponse = await response.text(); // Get the error message from the server
                    throw new Error(errorResponse);
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                errorParagraph.textContent = error.message;
                errorParagraph.classList.remove("error--hidden");
            });
    });
});
