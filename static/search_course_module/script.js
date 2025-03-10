document.addEventListener("DOMContentLoaded", function () {
    const modules = [];
    const moduleTableBody = document.getElementById("module-table");
    const deleteButtons = document.querySelectorAll(".delete-btn");
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

    for (const row of moduleTableBody.rows) {
        modules.push({
            module_id: row.cells[0].textContent.toLowerCase(),
            module_name: row.cells[1].textContent.toLowerCase(),
            module_description: row.cells[2].textContent.toLowerCase(),
        });
    }

    const moduleIdInput = document.getElementById("search-module-id");
    const moduleNameInput = document.getElementById("search-module-name");
    const moduleDescriptionInput = document.getElementById("search-module-description");

    const filterModules = () => {
        const filters = {
            module_id: moduleIdInput.value.toLowerCase(),
            module_name: moduleNameInput.value.toLowerCase(),
            module_description: moduleDescriptionInput.value.toLowerCase(),
        };

        for (const row of moduleTableBody.rows) {
            const module = modules[row.rowIndex - 1];
            let shouldShow = true;

            if (filters.module_id && !module.module_id.includes(filters.module_id))
                shouldShow = false;
            if (filters.module_name && !module.module_name.includes(filters.module_name))
                shouldShow = false;
            if (filters.module_description && !module.module_description.includes(filters.module_description))
                shouldShow = false;

            row.style.display = shouldShow ? "" : "none";
        }
    };

    moduleIdInput.addEventListener("input", filterModules);
    moduleNameInput.addEventListener("input", filterModules);
    moduleDescriptionInput.addEventListener("input", filterModules);

    deleteButtons.forEach((deleteButton) => {
        deleteButton.addEventListener("click", async () => {
            const moduleId = deleteButton.getAttribute("data-id");
            const row = deleteButton.closest("tr");
            const moduleName = row.cells[1].textContent.trim();

            if (confirm(`Are you sure you want to delete the module "${moduleName}"?`)) {
                try {
                    const response = await fetch(`/course_modules/delete?uuid=${moduleId}`, {
                        method: "DELETE",
                    });

                    if (response.ok) {
                        row.remove();
                    } else {
                        let errorMessage = await response.text();
                        console.error(errorMessage);
                        alert("Error: " + errorMessage);
                    }
                } catch (error) {
                    console.error(error);
                    alert("Failed to delete the module.");
                }
            }
        });
    });


});