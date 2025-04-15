document.addEventListener("DOMContentLoaded", function () {
    const xlsForm = document.forms["upload_xls_form"];

    xlsForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        const formData = new FormData(xlsForm);
        const response = await fetch("/students/upload", {
            method: "POST",
            body: formData,
        });

        if (response.ok) {
            const data = await response.json();
            alert(data.message);
            window.location.href = "/students/search";
        } else {
            console.log("Error");
            let responseText = await response.json();
            alert("Error: " + responseText.error);
        }
    });
});
