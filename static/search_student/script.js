document.addEventListener("DOMContentLoaded", () => {
    const searchForm = document.getElementById("searchForm");
    const studentTable = document.getElementById("student-table");
    const deleteButtons = document.querySelectorAll(".delete-button");
    const students = [];

    for (const row of studentTable.rows) {
        students.push({
            first_name: row.cells[0].innerText.toLowerCase(),
            last_name: row.cells[1].innerText.toLowerCase(),
            email: row.cells[2].innerText.toLowerCase(),
            student_id: row.cells[3].innerText,
            course_id: row.cells[4].innerText,
            skills: row.cells[5].dataset.skills
                .toLowerCase()
                .split(", ")
                .filter(Boolean),
            modules: row.cells[6].dataset.modules
                .toLowerCase()
                .split(", ")
                .filter(Boolean),
        });
    }

    searchForm.addEventListener("submit", (event) => {
        event.preventDefault();
        const formData = new FormData(searchForm);
        const filters = {
            first_name: formData.get("first_name").toLowerCase(),
            last_name: formData.get("last_name").toLowerCase(),
            email: formData.get("email").toLowerCase(),
            student_id: formData.get("student_id").toLowerCase(),
            course_id: formData.get("course"),
            skills: formData
                .getAll("skills")
                .map((skill) => skill.toLowerCase()),
            modules: formData
                .getAll("modules")
                .map((module) => module.toLowerCase()),
        };

        for (const row of studentTable.rows) {
            const student = students[row.rowIndex - 1];
            let shouldShow = true;

            if (
                filters.first_name &&
                !student.first_name.includes(filters.first_name)
            )
                shouldShow = false;
            if (
                filters.last_name &&
                !student.last_name.includes(filters.last_name)
            )
                shouldShow = false;
            if (filters.email && !student.email.includes(filters.email))
                shouldShow = false;
            if (
                filters.student_id &&
                !student.student_id.includes(filters.student_id)
            )
                shouldShow = false;
            if (filters.course_id && student.course_id !== filters.course_id)
                shouldShow = false;
            if (
                filters.skills.length &&
                !filters.skills.every((skill) => student.skills.includes(skill))
            )
                shouldShow = false;
            if (
                filters.modules.length &&
                !filters.modules.every((module) =>
                    student.modules.includes(module)
                )
            )
                shouldShow = false;

            row.style.display = shouldShow ? "" : "none";
        }
    });

    document.querySelectorAll(".toggle-btn").forEach((btn) => {
        btn.addEventListener("click", (event) => {
            event.preventDefault();
            const targetId = btn.getAttribute("data-bs-target");
            const targetElement = document.querySelector(targetId);

            targetElement.addEventListener("shown.bs.collapse", () => {
                btn.textContent = "Show Less";
            });

            targetElement.addEventListener("hidden.bs.collapse", () => {
                btn.textContent = "Show More";
            });
        });
    });

    for (const deleteButton of deleteButtons) {
        deleteButton.addEventListener("click", async () => {
            const studentId = deleteButton.getAttribute("data-id");
            if (confirm("Are you sure you want to delete this student?")) {
                const response = await fetch(
                    `/students/delete_student/${studentId}`,
                    { method: "DELETE" }
                );
                if (response.ok) {
                    window.location.reload();
                } else {
                    alert("Failed to delete the student.");
                }
            }
        });
    }
});
