let form = document.getElementsByClassName("login_form");
let error_paragragh = document.getElementById("error_message");

form.addEventListener("submit", function (e) {
    e.preventDefault();
    let formData = new FormData(form);
    let xhr = new XMLHttpRequest();
    xhr.open("POST", "/user/login_attempt", true);
    xhr.onload = function () {
        if (xhr.status === 200) {
            window.location.href = "/";
        }
        if (xhr.status === 401) {
            error_paragragh.textContent = "Incorrent login details";
        }
    };
    xhr.send(formData);
});
