document.addEventListener("DOMContentLoaded", () => {
    let form = document.querySelector(".login_form");
    let error_paragraph = document.querySelector(".error");
    let submitButton = form.querySelector("input[type='submit']");
    let otpModal = document.getElementById("otpModal");
    let otpForm = document.getElementById("otpForm");
    let otpInput = document.getElementById("otpInput");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        submitButton.disabled = true;

        let formData = new FormData(form);

        try {
            const response = await fetch("/employers/login", {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                // Show OTP modal
                otpModal.style.display = "flex";
            } else {
                error_paragraph.textContent = "Email was invalid";
                error_paragraph.classList.remove("error--hidden");
            }
        } catch (error) {
            console.log(error);
            error_paragraph.textContent = "Invalid";
            error_paragraph.classList.remove("error--hidden");
        } finally {
            submitButton.disabled = false;
            otpInput.value = "";
        }
    });

    otpForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        let otp = otpInput.value;
        if (otp) {
            let otpFormData = new FormData();
            otpFormData.append("otp", otp);

            try {
                const otp_response = await fetch("/employers/otp", {
                    method: "POST",
                    body: otpFormData,
                });

                if (otp_response.ok) {
                    window.location.href = "/employers/home";
                } else {
                    error_paragraph.textContent = "OTP was invalid";
                    error_paragraph.classList.remove("error--hidden");

                    fetch("/signout");
                }
            } catch (error) {
                console.log(error);
                error_paragraph.textContent = "An error occurred";
                error_paragraph.classList.remove("error--hidden");
            } finally {
                hideOtpModal();
            }
        } else {
            error_paragraph.textContent = "OTP was empty";
            error_paragraph.classList.remove("error--hidden");
            fetch("/signout");
        }
    });

    window.cancelOtp = function () {
        error_paragraph.textContent = "OTP entry canceled.";
        error_paragraph.classList.remove("error--hidden");
        hideOtpModal();
        fetch("/signout");
    };

    function hideOtpModal() {
        otpModal.style.display = "none";

    }

    document.title = "SkillPilot - Employer Login";
});
