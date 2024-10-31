const csvForm = document.forms["upload_csv_form"];
const xlsForm = document.forms["upload_xls_form"];

csvForm.addEventListener("submit", function (event) {
    event.preventDefault();
    uploadFile(csvForm, "/students/upload_csv");
});

xlsForm.addEventListener("submit", function (event) {
    event.preventDefault();
    uploadFile(xlsForm, "/students/upload_xlsx");
});

function uploadFile(form, url) {
    const formData = new FormData(form);
    fetch(url, {
        method: "POST",
        body: formData,
    })
        .then((response) => {
            if (response.ok) {
                alert(response.text());
            } else {
                alert("Error: " + response.json().data.error);
            }
        })
        .then((response) => response.json())
        .catch((error) => {
            console.error("Error:", error);
            alert("An error occurred while uploading the file");
        });
}
