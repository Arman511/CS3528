document.addEventListener("DOMContentLoaded", () => {
    const searchForm = document.getElementById("searchForm");
    const studentTable = document.getElementById("student-table");
    const deleteButtons = document.querySelectorAll(".delete-button");
    const students = [];
    for (row of studentTable.rows) {
        students.push({
            first_name: row.cells[0].innerText.toLowerCase(),
            last_name: row.cells[1].innerText.toLowerCase(),
            email: row.cells[2].innerText.toLowerCase(),
            student_id: row.cells[3].innerText,
            course_id: row.cells[4].innerText,
            skills: row.cells[5].innerText
                .split("\n")
                .filter((skill) => skill.trim() !== ""),
            modules: row.cells[6].innerText
                .split("\n")
                .filter((module) => module.trim() !== ""),
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
            skills: formData.getAll("skills"),
            modules: formData.getAll("modules"),
        };

        for (const row of studentTable.rows) {
            const student = students[row.rowIndex - 1];
            let shouldShow = true;

            if (
                filters.first_name &&
                !student.first_name.toLowerCase().includes(filters.first_name)
            ) {
                shouldShow = false;
            }
            if (
                filters.last_name &&
                !student.last_name.toLowerCase().includes(filters.last_name)
            ) {
                shouldShow = false;
            }
            if (
                filters.email &&
                !student.email.toLowerCase().includes(filters.email)
            ) {
                shouldShow = false;
            }
            if (
                filters.student_id &&
                !student.student_id.toLowerCase().includes(filters.student_id)
            ) {
                shouldShow = false;
            }
            if (filters.course_id && student.course_id !== filters.course_id) {
                shouldShow = false;
            }
            if (
                filters.skills.length &&
                !filters.skills.every((skill) => student.skills.includes(skill))
            ) {
                shouldShow = false;
            }
            if (
                filters.modules.length &&
                !filters.modules.every((module) =>
                    student.modules.includes(module)
                )
            ) {
                shouldShow = false;
            }

            row.style.display = shouldShow ? "" : "none";
        }
    });

    for (const deleteButton of deleteButtons) {
        deleteButton.addEventListener("click", async () => {
            const studentId = deleteButton.getAttribute("data-id");
            if (confirm("Are you sure you want to delete this student?")) {
                const response = await fetch(
                    `/students/delete_student/${studentId}`,
                    {
                        method: "DELETE",
                    }
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
