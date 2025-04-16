document.addEventListener("DOMContentLoaded", function () {
    const searchForm = document.getElementById("searchForm");
    const opportunityTable = document.getElementById("opportunity-table");
    const toggleButton = document.getElementById("toggleMore");
    const hiddenFields = document.querySelector(".hidden-fields");

    hiddenFields.style.display = "none";

    toggleButton.addEventListener("click", function () {
        if (hiddenFields.style.display === "none") {
            hiddenFields.style.display = "block";
            toggleButton.textContent = "Show Less";
        } else {
            hiddenFields.style.display = "none";
            toggleButton.textContent = "Show More";
        }
    });

    const opportunities = [];
    for (row of opportunityTable.rows) {
        opportunities.push({
            title: row.cells[0].innerText.toLowerCase(),
            description: row.cells[1].innerText.toLowerCase(),
            company: row.cells[2].innerText.toLowerCase(),
            url: row.cells[3].innerText.toLowerCase(),
            location: row.cells[4].innerText.toLowerCase(),
            courses_required: row.cells[5].dataset.courses.toLowerCase().split(", ").filter(Boolean),
            modules_required: row.cells[6].dataset.modules.toLowerCase().split(", ").filter(Boolean),
            spots_available: parseInt(row.cells[7].innerText.trim(), 10) || 0,
            duration: row.cells[8].innerText.trim().replace(" ", "_").toLowerCase(),
            ranked: row.cells[9].innerText.trim().toLowerCase(),
        });
    }

    const titleSearchInput = document.getElementById("title");
    const cnameSearchInput = document.getElementById("company");
    const descriptionSearchInput = document.getElementById("description");
    const locationSearchInput = document.getElementById("location");

    const spotsMinSearchInput = document.getElementById("spots_min");
    const spotsMaxSearchInput = document.getElementById("spots_max");
    const rankedSearchInput = document.getElementById("ranked");

    function filterOpportunities() {
        const titleValue = titleSearchInput.value.toLowerCase();
        const companyValue = cnameSearchInput ? cnameSearchInput.value.toLowerCase() : null;
        const descriptionValue = descriptionSearchInput.value.toLowerCase();
        const locationValue = locationSearchInput.value.toLowerCase();

        // Get values from Selectize inputs
        let courseValue = $("#course").val() || [];
        let modulesValue = $("#modules").val() || [];
        let durationValue = $("#placement_duration").val();

        courseValue = courseValue.map((course) => course.toLowerCase());
        modulesValue = modulesValue.map((module) => module.toLowerCase());
        durationValue = durationValue ? durationValue.toLowerCase() : null;

        const spotsMinValue = parseInt(spotsMinSearchInput.value, 10) || 0;
        const spotsMaxValue = parseInt(spotsMaxSearchInput.value, 10) || Number.MAX_SAFE_INTEGER;

        const rankedValue = rankedSearchInput ? rankedSearchInput.value.toLowerCase() : null;

        for (const row of opportunityTable.rows) {
            const opportunity = opportunities[row.rowIndex - 1];
            let shouldShow = true;

            if (titleValue && !opportunity.title.includes(titleValue)) shouldShow = false;
            if (companyValue && !opportunity.company.includes(companyValue)) shouldShow = false;
            if (descriptionValue && !opportunity.description.includes(descriptionValue)) shouldShow = false;
            if (locationValue && !opportunity.location.includes(locationValue)) shouldShow = false;
            if (courseValue.length && !courseValue.every((course) => opportunity.courses_required.includes(course))) shouldShow = false;
            if (modulesValue.length && !modulesValue.every((module) => opportunity.modules_required.includes(module))) shouldShow = false;
            if (opportunity.spots_available < spotsMinValue || opportunity.spots_available > spotsMaxValue) shouldShow = false;
            if (durationValue && !durationValue.includes(opportunity.duration)) shouldShow = false;
            if (rankedValue && rankedValue !== opportunity.ranked) shouldShow = false;
            row.style.display = shouldShow ? "" : "none";
        }
    }

    // Attach event listeners
    titleSearchInput.addEventListener("input", filterOpportunities);
    if (cnameSearchInput) cnameSearchInput.addEventListener("input", filterOpportunities);
    descriptionSearchInput.addEventListener("input", filterOpportunities);
    locationSearchInput.addEventListener("input", filterOpportunities);
    spotsMinSearchInput.addEventListener("input", filterOpportunities);
    spotsMaxSearchInput.addEventListener("input", filterOpportunities);
    rankedSearchInput.addEventListener("input", filterOpportunities);

    // Initialize Selectize for the select elements
    $("#course").selectize({
        plugins: ["remove_button"],
        sortField: "text",
        dropdownParent: "body",
        onChange: filterOpportunities,
    });

    $("#modules").selectize({
        plugins: ["remove_button"],
        sortField: "text",
        dropdownParent: "body",
        onChange: filterOpportunities,
    });

    $("#placement_duration").selectize({
        plugins: ["remove_button"],
        sortField: "text",
        dropdownParent: "body",
        onChange: filterOpportunities,
    });
});

function toggleText(btn, target) {
    const element = document.querySelector(target);
    if (element.classList.contains("show")) {
        btn.textContent = "Show More";
    } else {
        btn.textContent = "Show Less";
    }
}
