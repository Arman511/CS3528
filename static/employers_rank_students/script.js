document.addEventListener("DOMContentLoaded", function () {
	const rankSelects = document.querySelectorAll('.student-rank');

	rankSelects.forEach(select => {
		select.addEventListener('change', function () {
			const selectedValue = this.value;

			rankSelects.forEach(otherSelect => {
				if (otherSelect !== this && otherSelect.value === selectedValue) {
					this.value = '';
					alert('You can only rank each student once');
				}
			});
		});
	});

	// Handle form submission
	const submitButton = document.getElementById("submit-students");
	const opportunityId = document.getElementById("opp_id").textContent;

	submitButton.addEventListener("click", async function () {
		const allRanks = document.getElementsByClassName("student-rank");
		let ranks = [];

		for (let i = 0; i < allRanks.length; i++) {
			if (allRanks[i].value !== "") {
				ranks.push([allRanks[i].value, allRanks[i].id]);
			}
		}

		ranks.sort((a, b) => a[0] - b[0]);
		const actualRanks = ranks.map(rank => rank[1]);

		const formData = new FormData();
		formData.append("ranks", actualRanks);

		try {
			const response = await fetch(
				`/employers/rank_students?opportunity_id=${opportunityId}`,
				{
					method: "POST",
					body: formData,
				}
			);
			if (!response.ok) {
				throw new Error("An error occurred");
			}
			window.location.href = "/opportunities/search";
		} catch (error) {
			alert("An error occurred. Please try again later");
		}
	});
});

// ✅ Fix toggleText function
function toggleText(btn, target) {
	const element = document.querySelector(target);
	if (element) {
		element.classList.toggle('show');
		btn.textContent = element.classList.contains('show') ? 'Show Less' : 'Show More';
	}
}
