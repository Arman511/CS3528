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
                const response = await fetch("/user/matching", {
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
});
