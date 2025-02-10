document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".configure_form");

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const maxSkills = form.max_skills.value;
        const minNumRankingStudentToOpportunity = form.min_num_ranking_student_to_opportunity.value;
        let formData = new FormData();
        formData.append("max_skills", maxSkills);
        formData.append("min_num_ranking_student_to_opportunity", minNumRankingStudentToOpportunity);
        try {
            const response = await fetch("/superuser/configure", {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                alert("Configuration updated successfully");
            }
            else {
                let data = await response.json();
                alert(data.error);
            }

        }
        catch (error) {
            alert("An error occurred. Please try again later");
        }
    });
});