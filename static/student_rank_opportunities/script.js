document.addEventListener("DOMContentLoaded", function () {
    let submit_button = document.getElementById("submit-ranks");
    let url = window.location.href;
    let student_id = url.substring(url.lastIndexOf("/") + 1);
    let min_ranked = parseInt(document.getElementById("rank-opportunities-info").dataset.min_ranked, 10);
    submit_button.addEventListener("click", async function () {
        let all_ranks = document.getElementsByClassName("opportunity-rank");
        let ranks = [];
        for (let i = 0; i < all_ranks.length; i++) {
            if (all_ranks[i].value === "") {
                continue;
            }
            ranks.push([all_ranks[i].value, all_ranks[i].id]);
        }
        let len = all_ranks.length;
        if (ranks.length < min_ranked && all_ranks.length >= min_ranked) {
            alert("Please rank at least 5 or all of the opportunities");
            return;
        }
        ranks = ranks.sort((a, b) => a[0] - b[0]);
        let actual_ranks = [];
        for (let i = 0; i < ranks.length; i++) {
            actual_ranks.push(ranks[i][1]);
        }

        let formData = new FormData();
        formData.append("ranks", actual_ranks);
        try {
            const response = await fetch(
                `/students/rank_preferences/${student_id}`,
                {
                    method: "POST",
                    body: formData,
                }
            );
            if (!response.ok) {
                throw new Error("An error occurred");
            }
            window.location.href = "/students/update_success";
        } catch (error) {
            alert("An error occurred. Please try again later");
        }
    });
});
