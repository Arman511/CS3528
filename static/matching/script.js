document.addEventListener("DOMContentLoaded", function () {
    const sendEmailButtons = document.querySelectorAll(".send-email");

    sendEmailButtons.forEach((button) => {
        button.addEventListener("click", async function () {
            const student = this.getAttribute("data-student");
            const student_email = this.getAttribute("data-student-email");
            const employer_email = this.getAttribute("data-employer");
            const opportunity = this.getAttribute("data-opportunity");
            const responseElement = document.getElementById(
                `response-${student}`
            );
            const formData = new FormData();
            formData.append("student", student);
            formData.append("student_email", student_email);
            formData.append("employer_email", employer_email);
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
    const last_updated = document
        .getElementById("time-message")
        .getAttribute("data-last-updated");
    function updateTimeUntilNextUpdate() {
        const lastUpdated = new Date(last_updated);
        const now = new Date();
        const fiveMinutes = 5 * 60 * 1000;
        const nextUpdate = new Date(lastUpdated.getTime() + fiveMinutes);
        const timeUntilUpdate = Math.max(0, nextUpdate - now);
        const minutesUntilUpdate = Math.floor(timeUntilUpdate / (60 * 1000));
        const secondsUntilUpdate = Math.floor(
            (timeUntilUpdate % (60 * 1000)) / 1000
        );
        document.getElementById(
            "time-until-update"
        ).innerText = ` (${minutesUntilUpdate} minutes and ${secondsUntilUpdate} seconds remaining)`;
    }

    setInterval(updateTimeUntilNextUpdate, 1000);
    updateTimeUntilNextUpdate();

    const deleteButtons = document.querySelectorAll(".delete-button");

    deleteButtons.forEach((button) => {
        button.addEventListener("click", async function () {
            const studentId = this.getAttribute("data-target");
            const row = this.closest("tr");

            console.log(`Delete student with ID: ${studentId}`);
            try {
                const response = await fetch(
                    `/students/delete_student/${studentId}`,
                    {
                        method: "DELETE",
                    }
                );

                if (response.ok) {
                    row.remove();
                    console.log(
                        `Student with ID: ${studentId} deleted successfully`
                    );
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
        for (const button of sendEmailButtons) {
            await new Promise((resolve) => setTimeout(resolve, 100));
            await button.click();
        }
    });
});
