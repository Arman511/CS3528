document.addEventListener("DOMContentLoaded", () => {
    const studentTable = document.getElementById("student-table");
    const deleteButtons = document.querySelectorAll(".delete-button");
    const students = [];
    const toggleButton = document.getElementById("toggleMore");
    const hiddenFields = document.querySelector(".hidden-fields");

    hiddenFields.style.display = "none";

    toggleButton.addEventListener("click", function () {
        if (hiddenFields.style.display === "none") {
            hiddenFields.style.display = "block";
            toggleButton.textContent = "Show Less";
        } else {
            hiddenFields.style.display = "none";
            toggleButton.textContent = "Show More";
        }
    });

    for (const row of studentTable.rows) {
        students.push({
            first_name: row.cells[0].innerText.toLowerCase() || "",
            last_name: row.cells[1].innerText.toLowerCase() || "",
            email: row.cells[2].innerText.toLowerCase() || "",
            student_id: row.cells[3].innerText || "",
            course_id: row.cells[4].innerText.toLowerCase() || "",
            skills: (row.cells[5].dataset.skills || "").toLowerCase().split(", ").filter(Boolean),
            modules: (row.cells[6].dataset.modules || "").toLowerCase().split(", ").filter(Boolean),
            ranked: row.cells[7].innerText.toLowerCase() || "",
        });
    }

    const firstNameInput = document.getElementById("first_name");
    const lastNameInput = document.getElementById("last_name");
    const emailInput = document.getElementById("email");
    const studentIdInput = document.getElementById("student_id");
    const courseSelect = document.getElementById("course");
    const skillsSelect = document.getElementById("skills");
    const modulesSelect = document.getElementById("modules");
    const rankedSelect = document.getElementById("ranked");

    function filterOptions() {
        const firstNameValue = firstNameInput.value.toLowerCase();
        const lastNameValue = lastNameInput.value.toLowerCase();
        const emailValue = emailInput.value.toLowerCase();
        const studentIdValue = studentIdInput.value.toLowerCase();
        const courseValue = courseSelect ? courseSelect.value.toLowerCase() : "";
        let skillsValue = $("#skills").val() || [];
        let modulesValue = $("#modules").val() || [];

        skillsValue = skillsValue.map((skill) => skill.toLowerCase());
        modulesValue = modulesValue.map((module) => module.toLowerCase());

        const rankedValue = rankedSelect.value.toLowerCase();

        for (const row of studentTable.rows) {
            const student = students[row.rowIndex - 1];
            let shouldShow = true;

            if (firstNameValue && !student.first_name.includes(firstNameValue)) shouldShow = false;
            if (lastNameValue && !student.last_name.includes(lastNameValue)) shouldShow = false;
            if (emailValue && !student.email.includes(emailValue)) shouldShow = false;
            if (studentIdValue && !student.student_id.includes(studentIdValue)) shouldShow = false;
            if (courseValue && student.course_id !== courseValue) shouldShow = false;
            if (skillsValue.length && !skillsValue.every((skill) => student.skills.includes(skill))) shouldShow = false;
            if (modulesValue.length && !modulesValue.every((module) => student.modules.includes(module))) shouldShow = false;
            if (rankedValue && student.ranked !== rankedValue) shouldShow = false;

            row.style.display = shouldShow ? "" : "none";
        }
    }

    firstNameInput.addEventListener("input", filterOptions);
    lastNameInput.addEventListener("input", filterOptions);
    emailInput.addEventListener("input", filterOptions);
    studentIdInput.addEventListener("input", filterOptions);
    rankedSelect.addEventListener("input", filterOptions);

    $("#skills").selectize({
        plugins: ["remove_button"],
        maxItems: 10,
        sortField: "text",
        dropdownParent: "body",
        onChange: filterOptions,
    });
    $("#modules").selectize({
        plugins: ["remove_button"],
        sortField: "text",
        dropdownParent: "body",
        onChange: filterOptions,
    });
    $("#course").selectize({
        sortField: "text",
        dropdownParent: "body",
        onChange: filterOptions,
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
                const response = await fetch(`/students/delete_student/${studentId}`, { method: "DELETE" });
                if (response.ok) {
                    window.location.reload();
                } else {
                    alert("Failed to delete the student.");
                }
            }
        });
    }
});
