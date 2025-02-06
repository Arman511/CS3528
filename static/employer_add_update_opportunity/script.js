document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector(".update_add_form");
    const errorParagraph = document.querySelector(".error");
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        let _id = document.getElementById("_id").value;
        let title = document.getElementById("title").value;
        let description = document.getElementById("description").value;
        let selectedCourses = [];
        let courseSelect = document.getElementById("course");
        for (let i = 0; i < courseSelect.options.length; i++) {
            if (courseSelect.options[i].selected) {
                selectedCourses.push(courseSelect.options[i].value);
            }
        }
        let url = document.getElementById("url").value;
        let location = document.getElementById("location").value;
        let placement_duration =
            document.getElementById("placement_duration").value;
        let selectedModules = [];
        let spots_available = document.getElementById("spots_available").value;
        let modulesSelect = document.getElementById("modules");
        for (let i = 0; i < modulesSelect.options.length; i++) {
            if (modulesSelect.options[i].selected) {
                selectedModules.push(modulesSelect.options[i].value);
            }
        }
        let formData = new FormData();
        formData.append("_id", _id);
        formData.append("title", title);
        formData.append("description", description);
        formData.append("courses_required", JSON.stringify(selectedCourses));
        formData.append("url", url);
        formData.append("location", location);
        formData.append("duration", placement_duration);
        formData.append("modules_required", JSON.stringify(selectedModules));
        formData.append("spots_available", spots_available);
        formData.append("employer_id", document.querySelector(".employer_id").getAttribute("employer_id"));

        try {
            const response = await fetch(
                "/opportunities/employer_add_update_opportunity",
                { method: "POST", body: formData }
            );
            if (response.ok) {
                alert("Opportunity added/updated.");
                errorParagraph.classList.add("error--hidden");
                window.location.href = "/opportunities/search";
            } else {
                errorParagraph.textContent =
                    "Error adding/updating opportunity.";
                errorParagraph.classList.remove("error--hidden");
            }
        } catch (error) {
            console.error("Error:", error);
            errorParagraph.textContent = "Error adding/updating opportunity.";
            errorParagraph.classList.remove("error--hidden");
        }
    });
});
