document.addEventListener("DOMContentLoaded", function () {
    const sendEmailButtons = document.querySelectorAll(".send-email");
    const sendAllEmailsButton = document.getElementById("send-all-emails");
    const loadingOverlay = document.createElement("div");
    loadingOverlay.id = "loading-overlay";
    loadingOverlay.style.display = "none";
    loadingOverlay.style.position = "fixed";
    loadingOverlay.style.top = "0";
    loadingOverlay.style.left = "0";
    loadingOverlay.style.width = "100%";
    loadingOverlay.style.height = "100%";
    loadingOverlay.style.backgroundColor = "rgba(0, 0, 0, 0.5)";
    loadingOverlay.style.zIndex = "9999";
    loadingOverlay.style.color = "white";
    loadingOverlay.style.textAlign = "center";
    loadingOverlay.style.paddingTop = "20%";
    loadingOverlay.innerHTML = `
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%;">
            <div class="spinner" style="border: 4px solid rgba(255, 255, 255, 0.3); border-top: 4px solid white; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite;"></div>
            <p>Loading...</p>
        </div>
        <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    `;
    document.body.appendChild(loadingOverlay);

    function showLoading() {
        loadingOverlay.style.display = "block";
    }

    function hideLoading() {
        loadingOverlay.style.display = "none";
    }

    sendEmailButtons.forEach((button) => {
        button.addEventListener("click", async function () {
            if (!confirm("Please confirm that you want to send the email to the student.")) {
                return;
            }
            showLoading();
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
            } finally {
                hideLoading();
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

    sendAllEmailsButton.addEventListener("click", async function () {
        if (!confirm("Please confirm that you want to send the email to the student.")) {
            return;
        }
        showLoading();
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
        } finally {
            hideLoading();
        }
    });
});
