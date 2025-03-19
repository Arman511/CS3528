document.addEventListener("DOMContentLoaded", function () {
    let email = document.getElementById("email");
    let password = document.getElementById("password");
    let submit = document.querySelector("#submit");

    let error_paragraph = document.querySelector(".error");

    submit.addEventListener("click", async function (event) {
        event.preventDefault(); // Prevent default form submission
        let formData = new FormData();
        formData.set("email", email.value);
        formData.set("password", password.value);

        if (email.value === "" || password.value === "") {
            error_paragraph.textContent = "Please fill in all fields";
            error_paragraph.classList.remove("error--hidden");
        }

        if (email.value !== "" && password.value !== "") {
            error_paragraph.classList.add("error--hidden");
        }

        try {
            const response = await fetch("/user/login", {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                let data = await response.json();
                window.location.href = data.message;
            } else if (response.status === 401 || response.status === 400) {
                let errorResponse = await response.json(); // Parse JSON response
                fetch("/signout");
                throw new Error(errorResponse.error); // Throw error with the extracted message
            } else {
                fetch("/signout");
                throw new Error("Server error"); // General server error message
            }
        } catch (error) {
            console.error("Error:", error); // Log error to console
            error_paragraph.textContent = error.message; // Use `error.message` to display the error
            error_paragraph.classList.remove("error--hidden"); // Ensure the error paragraph is visible

        }
    });
    document.title = "SkillPilot - Placement Team Login";
});
