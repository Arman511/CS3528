document.addEventListener("DOMContentLoaded", function () {
    const sendEmailButtons = document.querySelectorAll(".send-email");

    sendEmailButtons.forEach((button) => {
        button.addEventListener("click", async function () {
            if (!confirm("Please confirm that you want to send the email to the student.")) {
                return;
            }
            const student = this.getAttribute("data-student");
            const opportunity = this.getAttribute("data-opportunity");
            const responseElement = document.getElementById(`response-${student}`);
            const formData = new FormData();
            formData.append("student", student);
            formData.append("opportunity", opportunity);
            try {
                const response = await fetch("/user/send_match_email", {
                    method: "POST",
                    body: formData,
                });

                const data = await response.json();
                if (response.ok) {
                    button.className = "btn btn-success send-email";
                    responseElement.textContent = data.message;
                    responseElement.className.append("text-success");
                } else {
                    console.error("Error:", response.statusText);
                    responseElement.textContent = data.error;
                    responseElement.className.append("text-danger");
                }
            } catch (error) {
                console.error("Error:", error);
            }
        });
    });

    const deleteButtons = document.querySelectorAll(".delete-button");

    deleteButtons.forEach((button) => {
        button.addEventListener("click", async function () {
            const studentId = this.getAttribute("data-target");
            const row = this.closest("tr");

            console.log(`Delete student with ID: ${studentId}`);
            try {
                const response = await fetch(`/students/delete_student/${studentId}`, {
                    method: "DELETE",
                });

                if (response.ok) {
                    row.remove();
                    console.log(`Student with ID: ${studentId} deleted successfully`);
                } else {
                    const error = await response.json();
                    console.error("Error:", error);
                    const errorElement = document.querySelector(".error");
                    errorElement.classList.remove("error--hidden");
                    errorElement.textContent = error.message;
                }
            } catch (error) {
                console.error("Fetch error:", error);
            }
        });
    });

    const sendAllEmailsButton = document.getElementById("send-all-emails");

    sendAllEmailsButton.addEventListener("click", async function () {
        if (!confirm("Please confirm that you want to send the email to the student.")) {
            return;
        }
        const students = [];
        const studentRows = document.querySelectorAll(".student-row");
        studentRows.forEach((row) => {
            const student = row.querySelector(".send-email").getAttribute("data-student");
            const opportunity = row.querySelector(".send-email").getAttribute("data-opportunity");
            students.push({ student, opportunity });
        });

        try {
            const response = await fetch("/user/send_all_emails", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ students }),
            });

            const data = await response.json();
            const responseElement = document.getElementById("response-all");
            if (response.ok) {
                console.log("All emails sent successfully");
                responseElement.textContent = data.message;
                responseElement.className = "text-success plain-center";
            } else {
                console.error("Error:", response.statusText);
                responseElement.textContent = data.error;
                responseElement.className = "text-danger plain-center";
            }
        } catch (error) {
            console.error("Fetch error:", error);
            const responseElement = document.getElementById("response-all");
            responseElement.textContent = "An error occurred while sending emails.";
            responseElement.className = "text-danger plain-center";
        }
    });
});
