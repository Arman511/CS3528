document.addEventListener("DOMContentLoaded", () => {
    const searchForm = document.getElementById("searchForm");
    const studentTable = document.getElementById("student-table");

    if (!searchForm || !studentTable) {
        console.error("Search form or student table element not found.");
        return;
    }

    // Event listener for the search form submission
    searchForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const formData = new FormData(searchForm);
        const formObject = {};

        // Convert FormData to a plain object
        formData.forEach((value, key) => {
            if (formObject[key]) {
                formObject[key] = [].concat(formObject[key], value);
            } else {
                formObject[key] = value;
            }
        });

        // Filter out empty fields to send only filled ones
        const filteredFormObject = Object.fromEntries(
            Object.entries(formObject).filter(
                ([_, value]) => value && value.length > 0
            )
        );

        try {
            const response = await fetch("/students/search_students", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(filteredFormObject),
            });

            if (response.ok) {
                const students = await response.json();
                console.log("Students found:", students);

                // Clear existing rows
                studentTable.innerHTML = "";
                // Display the students in the table
                students.forEach((student) => {
                    const row = document.createElement("tr");

                    // Create editable fields for updating student info
                    row.innerHTML = `
                        <td><span data-field="first_name">${student.first_name}</span></td>
                        <td><span data-field="last_name">${student.last_name}</span></td>
                        <td><span data-field="email">${student.email}</span></td>
                        <td><span data-field="student_id">${student.student_id}</span></td>
                        <td><span data-field="course">${student.course}</span></td>
                        <td>
                            <a href="/students/update_student/${student.student_id}">
                                <button class="btn btn-info btn-sm update-button mb-2" data-id="${student.student_id}">Update</button>
                            </a>
                            <button class="btn btn-info btn-sm delete-button" data-id="${student.student_id}">Delete</button>
                        </td>
                    `;

                    // Add event listeners for the button
                    const deleteButton = row.querySelector(".delete-button");

                    // Handle deleting the student
                    deleteButton.addEventListener("click", async () => {
                        const studentId = deleteButton.getAttribute("data-id");

                        // Show a confirmation dialog
                        const userConfirmed = confirm(
                            `Are you sure you want to delete the student with ID: ${studentId}?`
                        );

                        if (!userConfirmed) {
                            // If the user selects "No", cancel the operation
                            alert("Deletion canceled.");
                            return;
                        }

                        try {
                            const deleteResponse = await fetch(
                                `/students/delete_student/${studentId}`,
                                {
                                    method: "DELETE",
                                }
                            );

                            if (deleteResponse.ok) {
                                row.remove();
                                alert(
                                    `Student with ID: ${studentId} deleted successfully.`
                                );
                            } else {
                                const error = await deleteResponse.json();
                                const errorElement =
                                    document.querySelector(".error");
                                if (errorElement) {
                                    errorElement.classList.remove(
                                        "error--hidden"
                                    );
                                    errorElement.textContent =
                                        error.message ||
                                        "Failed to delete student.";
                                }
                                alert("Failed to delete student.");
                            }
                        } catch (deleteError) {
                            console.error("Delete error:", deleteError);
                            const errorElement =
                                document.querySelector(".error");
                            if (errorElement) {
                                errorElement.classList.remove("error--hidden");
                                errorElement.textContent =
                                    "An error occurred while deleting the student. Please try again.";
                            }
                            alert(
                                "An error occurred while deleting the student."
                            );
                        }
                    });

                    // Append the row to the student table
                    studentTable.appendChild(row);
                });
            } else {
                const error = await response.json();
                const errorElement = document.querySelector(".error");
                if (errorElement) {
                    errorElement.classList.remove("error--hidden");
                    errorElement.textContent =
                        error.message || "Failed to fetch students.";
                }
            }
        } catch (fetchError) {
            const errorElement = document.querySelector(".error");
            if (errorElement) {
                errorElement.classList.remove("error--hidden");
                errorElement.textContent =
                    "An error occurred while searching. Please try again.";
            }
        }
    });
});
