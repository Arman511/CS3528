document.addEventListener("DOMContentLoaded", function () {
    let form = document.querySelector(".employer_adding_form");
    let errorParagraph = document.querySelector(".error");

    form.addEventListener("submit", async function (event) {
        let formData = new FormData(form);
        event.preventDefault();
        try {
            const response = await fetch("/employers/add_employer", {
                method: "POST",
                body: formData,
            });
            if (response.ok) {
                alert("Employer added successfully");
                errorParagraph.classList.add("error--hidden");
            } else {
                errorParagraph.textContent = "Error adding employer";
                errorParagraph.classList.remove("error--hidden");
            }
        } catch (error) {
            console.error("Error:", error);
            errorParagraph.textContent = error.message;
            errorParagraph.classList.remove("error--hidden");
        }
    });
});
