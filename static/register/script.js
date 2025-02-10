document.addEventListener("DOMContentLoaded", () => {
    // Select the password fields and eye icons
    const passwordField = document.getElementById("passwordField");
    const confirmPasswordField = document.getElementById(
        "confirmPasswordField"
    );

    const error_paragraph = document.querySelector(".error");
    const register_form = document.querySelector(".register_form");

    // Form submission logic
    register_form.addEventListener("submit", async function (e) {
        e.preventDefault(); // Prevent form submission

        // Check if passwords match
        if (passwordField.value !== confirmPasswordField.value) {
            error_paragraph.textContent = "Passwords don't match, Try again.";
            error_paragraph.classList.remove("error--hidden");
            return; // Stop submission if passwords do not match
        }

        // Clear previous error message
        error_paragraph.classList.add("error--hidden");

        let formData = new FormData(register_form);

        try {
            const response = await fetch("/user/register", {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                window.location.href = "/user/search";
            }
            else {
                let errorMessage = await response.text();
                console.error("Error:", errorMessage);
                error_paragraph.classList.remove("error--hidden");
                error_paragraph.textContent = errorMessage;
            }
        }
        catch (error) {
            console.error("Error:", error);
            error_paragraph.classList.remove("error--hidden");
            error_paragraph.textContent = "An error occurred while registering the user.";
        }


    });
});
