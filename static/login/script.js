let form = document.querySelector(".login_form");
let error_paragraph = document.querySelector(".error");

form.addEventListener("submit", function (e) {
    e.preventDefault();
    let formData = new FormData(form);

    fetch("/user/login_attempt", {
        method: "POST",
        body: formData,
    })
        .then( async (response) => {
            if (response.ok) {
                window.location.href = "/";
            } else if (response.status === 401 || response.status === 400) {
                throw new Error(await response.text());
            } else {
                throw new Error("Server error");
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            error_paragraph.textContent = error;
            error_paragraph.classList.remove("error--hidden");
        });
});
