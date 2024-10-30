document.addEventListener("DOMContentLoaded", async () => {
    let form = document.querySelector(".login_form");
    let error_paragraph = document.querySelector(".error");
    let formData = new FormData();

    formData.append("email", formData);

    try {
        const response = await fetch("/employers/login", {
            method: "POST",
            body: formData,
        });

        if (response.ok) {
            let otp = prompt("Enter the OTP sent to your email");
            let formData = new FormData();
            formData.append("otp", otp);
            const otp_response = await fetch("/employers/login_otp", {
                method: "POST",
                body: formData,
            });

            if (otp_response.ok) {
                window.location.href = "/employers/home";
            } else {
                error_paragraph.textContent = "OTP was invalid";
                error_paragraph.classList.remove("error--hidden");
            }
        } else {
            error_paragraph.textContent = "Email was invalid";
            error_paragraph.classList.remove("error--hidden");
        }
    } catch (error) {
        console.log(error);
        error_paragraph.textContent = "Invalid";
        error_paragraph.classList.remove("error--hidden");
    }
});
