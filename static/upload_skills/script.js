document.addEventListener("DOMContentLoaded", function () {
    const form = document.forms["upload_xls_form"];
    const errorElement = document.querySelector(".error");
    const subButton = document.getElementById("upload_button");

    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        subButton.disabled = true;
        const fileInput = form.elements["file"];
        const file = fileInput.files[0];

        if (!file) {
            showError("No file selected");
            return;
        }

        if (!isValidFileType(file)) {
            showError("Invalid file type. Please upload an XLSX or XLS file.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);
        try {
            const response = await fetch("/skills/upload", {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                window.location.href = "/skills/search";
            } else {
                let data = await response.json();
                showError(data.error);
            }
        } catch (error) {
            showError("An error occurred while uploading the file. Please try again.");
        }
        subButton.disabled = false;
        form.reset();
    });

    function showError(message) {
        errorElement.textContent = message;
        errorElement.classList.remove("error--hidden");
    }

    function isValidFileType(file) {
        const allowedExtensions = ["xlsx", "xls"];
        const fileExtension = file.name.split(".").pop().toLowerCase();
        return allowedExtensions.includes(fileExtension);
    }
});
