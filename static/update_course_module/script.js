document.addEventListener("DOMContentLoaded", function () {
    const uuid = document.getElementById("_id").getAttribute("data-id");
    const form = document.querySelector(".update-module-form");

    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        let formData = new FormData();
        const module_id = document.getElementById("module_id").value;
        const module_name = document.getElementById("module_name").value;
        const module_description = document.getElementById("module_description").value;
        formData.append("module_id", module_id);
        formData.append("module_name", module_name);
        formData.append("module_description", module_description);

        try {
            const response = await fetch(`/course_modules/update?uuid=${uuid}`, {
                method: "POST",
                body: formData,
            });
            if (response.ok) {
                window.location.href = "/course_modules/search";
            } else {
                alert("Failed to update module");
            }
        } catch (error) {
            console.error(error);
            alert("Failed to update module");
        }
    });
});