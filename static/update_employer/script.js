document.addEventListener("DOMContentLoaded", function () {
    const updateForm = document.getElementById("updateForm");
    const errorElement = document.querySelector(".error");
    updateForm.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent page reload
        // Collect form data
        const employerId = document.getElementById("employer_id").value;
        const companyName = document.getElementById("company_name").value.trim();
        const email = document.getElementById("email").value.trim();
        if (!companyName || !email) {
            errorElement.textContent = "All fields are required.";
            errorElement.classList.remove("error--hidden");
            return;
        }
        // Send update request
        fetch("/employers/update_employer", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({
                employer_id: employerId,
                company_name: companyName,
                email: email
            })
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.error) {
                    errorElement.textContent = data.error;
                    errorElement.classList.remove("error--hidden");
                } else {
                    alert("Employer updated successfully!");
                    window.location.href = "/employers/search_employers"; // Redirect back
                }
            })
            .catch(() => {
                errorElement.textContent = "An error occurred. Please try again.";
                errorElement.classList.remove("error--hidden");
            });
    });
});