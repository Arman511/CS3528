document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".deadline_form");
    const errorElement = document.querySelector(".error");

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        const detailsDeadline = new Date(
            document.getElementById("details_deadline").value
        );
        const studentRankingDeadline = new Date(
            document.getElementById("student_ranking_deadline").value
        );
        const opportunitiesRankingDeadline = new Date(
            document.getElementById("opportunities_ranking_deadline").value
        );

        if (detailsDeadline >= studentRankingDeadline) {
            errorElement.textContent =
                "Details deadline must be before student ranking deadline.";
            errorElement.classList.remove("error--hidden");
            return;
        }

        if (studentRankingDeadline >= opportunitiesRankingDeadline) {
            errorElement.textContent =
                "Student ranking deadline must be before opportunities ranking deadline.";
            errorElement.classList.remove("error--hidden");
            return;
        }

        const formData = new FormData(form);

        errorElement.classList.add("error--hidden");

        fetch("/user/deadline", {
            method: "POST",
            body: formData,
        })
            .then(async (response) => {
                if (response.ok) {
                    alert("Deadline updated");
                } else if (response.status === 401 || response.status === 400) {
                    const errorResponse = await response.json();
                    throw new Error(errorResponse.error);
                } else {
                    throw new Error("Server error");
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                errorElement.textContent = error.message;
                errorElement.classList.remove("error--hidden");
            });
    });
});
