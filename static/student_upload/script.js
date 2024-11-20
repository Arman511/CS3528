document.addEventListener("DOMContentLoaded", function () {
    const csvForm = document.forms["upload_csv_form"];
    const xlsForm = document.forms["upload_xls_form"];

    csvForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        const formData = new FormData(csvForm);
        const response = await fetch("/students/upload_csv", {
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
