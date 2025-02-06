document.addEventListener("DOMContentLoaded", () => {
    const searchForm = document.getElementById("searchForm");
    const courseTable = document.getElementById("course-table");

    if (!searchForm || !courseTable) {
        console.error("Search form or course table element not found.");
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
            const response = await fetch("/courses/search_courses", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(filteredFormObject),
            });

            if (response.ok) {
                const courses = await response.json();
                console.log("Courses found:", courses);

                // Clear existing rows
                courseTable.innerHTML = "";
                // Display the courses in the table
                courses.forEach((course) => {
                    const row = document.createElement("tr");

                    // Create editable fields for updating course info
                    row.innerHTML = `
                        <td><span data-field="course_id">${course.course_id}</span></td>
                        <td><span data-field="course_name">${course.course_name}</span></td>
                        <td>
                            <button class="btn btn-info btn-sm update-button mb-2" data-id="${course.course_id}">Update</button>
                            <button class="btn btn-info btn-sm delete-button" data-id="${course.course_id}">Delete</button>
                        </td>
                    `;

                    // Add event listeners for the buttons
                    const updateButton = row.querySelector(".update-button");
                    const deleteButton = row.querySelector(".delete-button");

                    // Handle updating the course data
                    updateButton.addEventListener("click", async () => {
                        const updatedData = {};

                        // Collect updated values from editable fields
                        row.querySelectorAll(".editable").forEach((input) => {
                            const newValue = input.value;
                            const oldValue = input.dataset.oldValue;

                            // Only update fields where the value has changed
                            if (newValue !== oldValue) {
                                updatedData[input.dataset.field] = newValue;
                            }
                        });

                        console.log("Updated course data:", updatedData); // Log the data being saved

                        if (Object.keys(updatedData).length === 0) {
                            alert("No changes made.");
                            return;
                        }

                        // Include course ID in the updated data
                        updatedData.course_id = course.course_id;

                        try {
                            const updateResponse = await fetch(
                                `/course/update_course/${course.course_id}`,
                                {
                                    method: "PUT", // Use PUT for updating the course
                                    headers: {
                                        "Content-Type": "application/json",
                                    },
                                    body: JSON.stringify(updatedData), // Send the updated data as JSON
                                }
                            );

                            if (updateResponse.ok) {
                                const result = await updateResponse.json();
                                console.log("Update response:", result); // Log the server response
                                alert(result.message); // Display success message

                                // Optionally, make fields readonly after saving
                                row.querySelectorAll(".editable").forEach(
                                    (input) => {
                                        input.setAttribute("readonly", "true");
                                    }
                                );
                                updateButton.textContent = "Updated"; // Change button text to "Updated"
                            } else {
                                const error = await updateResponse.json();
                                console.log("Update error response:", error); // Log the error response
                                alert(
                                    error.message || "Failed to update course."
                                );
                            }
                        } catch (updateError) {
                            console.error("Update error:", updateError);
                            alert(
                                "An error occurred while updating the course. Please try again."
                            );
                        }
                    });

                    // Handle deleting the course
                    deleteButton.addEventListener("click", async () => {
                        const courseId = deleteButton.getAttribute("data-id");

                        // Show a confirmation dialog
                        const userConfirmed = confirm(
                            `Are you sure you want to delete the course with ID: ${courseId}?`
                        );

                        if (!userConfirmed) {
                            // If the user selects "No", cancel the operation
                            alert("Deletion canceled.");
                            return;
                        }

                        try {
                            const deleteResponse = await fetch(
                                `/courses/delete_course/${courseId}`,
                                {
                                    method: "DELETE",
                                }
                            );

                            if (deleteResponse.ok) {
                                row.remove();
                                alert(
                                    `Course with ID: ${courseId} deleted successfully.`
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
                                        "Failed to delete course.";
                                }
                            }
                        } catch (deleteError) {
                            console.error("Delete error:", deleteError);
                            const errorElement =
                                document.querySelector(".error");
                            if (errorElement) {
                                errorElement.classList.remove("error--hidden");
                                errorElement.textContent =
                                    "An error occurred while deleting the course. Please try again.";
                            }
                        }
                    });

                    // Append the row to the course table
                    courseTable.appendChild(row);
                });
            } else {
                const error = await response.json();
                const errorElement = document.querySelector(".error");
                if (errorElement) {
                    errorElement.classList.remove("error--hidden");
                    errorElement.textContent =
                        error.message || "Failed to fetch courses.";
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