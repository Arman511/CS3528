document.addEventListener("DOMContentLoaded", function () {
    const uuid = document.getElementById("_id").getAttribute("data-id");
    const form = document.querySelector(".update-course-form");

    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        let formData = new FormData();
        const course_id = document.getElementById("course_id").value;
        const course_name = document.getElementById("course_name").value;
        const course_description = document.getElementById("course_description").value;
        formData.append("course_id", course_id);
        formData.append("course_name", course_name);
        formData.append("course_description", course_description);

        try {
            response = await fetch(`/courses/update?uuid=${uuid}`, {
                method: "POST",
                body: formData,
            });
            if (response.ok) {
                window.location.href = "/courses/search";
            } else {
                alert("Failed to update course");
            }
        } catch (error) {
            console.error(error);
            alert("Failed to update course");
        }
    });
});
