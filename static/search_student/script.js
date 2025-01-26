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
            Object.entries(formObject).filter(([_, value]) => value && value.length > 0)
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
                        <td><input type="text" class="editable" value="${student.first_name}" data-field="first_name" data-old-value="${student.first_name}"></td>
                        <td><input type="text" class="editable" value="${student.last_name}" data-field="last_name" data-old-value="${student.last_name}"></td>
                        <td><input type="email" class="editable" value="${student.email}" data-field="email" data-old-value="${student.email}"></td>
                        <td><input type="text" class="editable" value="${student.student_id}" data-field="student_id" data-old-value="${student.student_id}" readonly></td>
                        <td><input type="text" class="editable" value="${student.course}" data-field="course" data-old-value="${student.course}"></td>
                        <td>
                            <button class="update-button" data-id="${student.student_id}">Update</button>
                            <button class="delete-button" data-id="${student.student_id}">Delete</button>
                        </td>
                    `;

                    // Add event listeners for the buttons
                    const updateButton = row.querySelector(".update-button");
                    const deleteButton = row.querySelector(".delete-button");

                    // Handle updating the student data
                    updateButton.addEventListener("click", async () => {
                        const updatedData = {};

                        // Collect updated values from editable fields
                        row.querySelectorAll(".editable").forEach(input => {
                            const newValue = input.value;
                            const oldValue = input.dataset.oldValue;

                            // Only update fields where the value has changed
                            if (newValue !== oldValue) {
                                updatedData[input.dataset.field] = newValue;
                            }
                        });

                        console.log("Updated student data:", updatedData); // Log the data being saved

                        if (Object.keys(updatedData).length === 0) {
                            alert("No changes made.");
                            return;
                        }

                        // Include student ID in the updated data
                        updatedData.student_id = student.student_id;

                        try {
                            const updateResponse = await fetch(`/students/update_student/${student.student_id}`, {
                                method: "PUT",  // Use PUT for updating the student
                                headers: {
                                    "Content-Type": "application/json",
                                },
                                body: JSON.stringify(updatedData),  // Send the updated data as JSON
                            });

                            if (updateResponse.ok) {
                                const result = await updateResponse.json();
                                console.log("Update response:", result);  // Log the server response
                                alert(result.message);  // Display success message

                                // Optionally, make fields readonly after saving
                                row.querySelectorAll(".editable").forEach(input => {
                                    input.setAttribute("readonly", "true");
                                });
                                updateButton.textContent = "Updated";  // Change button text to "Updated"
                            } else {
                                const error = await updateResponse.json();
                                console.log("Update error response:", error);  // Log the error response
                                alert(error.message || "Failed to update student.");
                            }
                        } catch (updateError) {
                            console.error("Update error:", updateError);
                            alert("An error occurred while updating the student. Please try again.");
                        }
                    });

                    // Handle deleting the student
                    deleteButton.addEventListener("click", async () => {
                        const studentId = deleteButton.getAttribute("data-id");

                        // Show a confirmation dialog
                        const userConfirmed = confirm(`Are you sure you want to delete the student with ID: ${studentId}?`);

                        if (!userConfirmed) {
                            // If the user selects "No", cancel the operation
                            alert("Deletion canceled.");
                            return;
                        }

                        try {
                            const deleteResponse = await fetch(`/students/delete_student/${studentId}`, {
                                method: "DELETE",
                            });

                            if (deleteResponse.ok) {
                                row.remove();
                                alert(`Student with ID: ${studentId} deleted successfully.`);
                            } else {
                                const error = await deleteResponse.json();
                                const errorElement = document.querySelector(".error");
                                if (errorElement) {
                                    errorElement.classList.remove("error--hidden");
                                    errorElement.textContent = error.message || "Failed to delete student.";
                                }
                            }
                        } catch (deleteError) {
                            console.error("Delete error:", deleteError);
                            const errorElement = document.querySelector(".error");
                            if (errorElement) {
                                errorElement.classList.remove("error--hidden");
                                errorElement.textContent = "An error occurred while deleting the student. Please try again.";
                            }
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
                    errorElement.textContent = error.message || "Failed to fetch students.";
                }
            }
        } catch (fetchError) {
            const errorElement = document.querySelector(".error");
            if (errorElement) {
                errorElement.classList.remove("error--hidden");
                errorElement.textContent = "An error occurred while searching. Please try again.";
            }
        }
    });
});
