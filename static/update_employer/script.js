document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector(".update_employer_form");
    const errorParagraph = document.querySelector(".error");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        // Collect form data
        let employerId = document.getElementById("employer_id").value;
        let companyName = document.getElementById("company_name").value.trim();
        let email = document.getElementById("email").value.trim();

        // Validation
        if (!companyName || !email) {
            errorParagraph.textContent = "All fields are required.";
            errorParagraph.classList.remove("error--hidden");
            return;
        }

        // Create form data
        let formData = new FormData();
        formData.append("employer_id", employerId);
        formData.append("company_name", companyName);
        formData.append("email", email);

        try {
            const response = await fetch("/employers/update_employer", {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                alert(data.message || "Employer updated successfully.");
                errorParagraph.classList.add("error--hidden");
                window.location.href = "/employers/search"; // Redirect on success
            } else {
                const errorData = await response.json();
                errorParagraph.textContent =
                    errorData.error || "Error updating employer.";
                errorParagraph.classList.remove("error--hidden");
            }
        } catch (error) {
            console.error("Error:", error);
            errorParagraph.textContent = "Error updating employer.";
            errorParagraph.classList.remove("error--hidden");
        }
    });
});
