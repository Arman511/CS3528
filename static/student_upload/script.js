document.addEventListener("DOMContentLoaded", function () {
    const xlsForm = document.forms["upload_xls_form"];

    xlsForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        const formData = new FormData(xlsForm);
        const response = await fetch("/students/upload_xlsx", {
            method: "POST",
            body: formData,
        });

        if (response.ok) {
            const data = await response.json();
            alert(data.message);
        } else {
            console.log("Error");
            alert("Error: " + response.json().error);
        }
    });
});
