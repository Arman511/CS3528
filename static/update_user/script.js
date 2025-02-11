document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".user_adding_form");
    const errorElement = document.querySelector(".error");
    const userIdElement = document.getElementById("_id");

    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        const userId = userIdElement.getAttribute("data-id");
        const userName = document.getElementById("user_name").value;
        const userEmail = document.getElementById("user_email").value;

        let form = new FormData();

        form.append("name", userName);
        form.append("email", userEmail);
        try {
            const response = await fetch(`/user/update?uuid=${userId}`, {
                method: "POST",
                body: form,
            });
            const result = await response.json();
            if (response.ok) {
                window.location.href = "/user/search";
            } else {
                errorElement.textContent = result.message;
                errorElement.classList.remove("error--hidden");
            }
        } catch (error) {
            errorElement.textContent = "An error occurred while updating the user.";
            errorElement.classList.remove("error--hidden");
        }
    });
});