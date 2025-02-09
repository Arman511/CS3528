document.addEventListener("DOMContentLoaded", function () {
    const courses = [];
    const courseTableBody = document.getElementById("course-table");
    const deleteButtons = document.querySelectorAll(".delete-btn");

    for (const row of courseTableBody.rows) {
        courses.push({
            course_id: row.cells[0].textContent.toLowerCase(),
            course_name: row.cells[1].textContent.toLowerCase(),
            course_description: row.cells[2].textContent.toLowerCase(),
        });
    }

    const courseIdInput = document.getElementById("search-course-id");
    const courseNameInput = document.getElementById("search-course-name");
    const courseDescriptionInput = document.getElementById("search-course-description");

    const filterCourses = () => {
        const filters = {
            course_id: courseIdInput.value.toLowerCase(),
            course_name: courseNameInput.value.toLowerCase(),
            course_description: courseDescriptionInput.value.toLowerCase(),
        };

        for (const row of courseTableBody.rows) {
            const course = courses[row.rowIndex - 1];
            let shouldShow = true;

            if (filters.course_id && !course.course_id.includes(filters.course_id))
                shouldShow = false;
            if (filters.course_name && !course.course_name.includes(filters.course_name))
                shouldShow = false;
            if (filters.course_description && !course.course_description.includes(filters.course_description))
                shouldShow = false;

            row.style.display = shouldShow ? "" : "none";
        }
    };

    courseIdInput.addEventListener("input", filterCourses);
    courseNameInput.addEventListener("input", filterCourses);
    courseDescriptionInput.addEventListener("input", filterCourses);


    deleteButtons.forEach((deleteButton) => {
        deleteButton.addEventListener("click", async () => {
            const courseId = deleteButton.getAttribute("data-id");
            const row = deleteButton.closest("tr");
            const courseName = row.cells[1].textContent.trim();

            if (confirm(`Are you sure you want to delete the course "${courseName}"?`)) {
                try {
                    const response = await fetch(`/courses/delete?uuid=${courseId}`, {
                        method: "DELETE",

                    });

                    if (response.ok) {
                        row.remove();
                    } else {
                        let errorMessage = await response.text();
                        console.error(errorMessage);
                        alert("error: " + errorMessage);
                    }
                } catch (error) {
                    console.error(error);
                    alert("Failed to delete the course.");
                }
            }
        });
    });
});
