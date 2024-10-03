let register_form = document.querySelector(".register_form");

let error_paragraph = document.querySelector(".error");

register_form.addEventListener("submit", function (e) {
    e.preventDefault();
    let formData = new FormData(register_form);

    fetch("/user/register_attempt", {
        method: "POST",
        body: formData,
    })
        .then(async (response) => {
            if (response.ok) {
                window.location.href = "/";
            } else if (response.status === 400) {
                throw new Error(await response.text());
            } else {
                throw new Error("Server error");
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            error_paragraph.classList.remove("error--hidden");
            error_paragraph.textContent = error;
        });
});
