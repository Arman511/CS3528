document.addEventListener("DOMContentLoaded", function () {
    const click_sfx = new Audio("/static/sfx/click.mp3");

    const buttons = document.querySelectorAll("button, .btn");

    buttons.forEach((button) => {
        button.addEventListener("click", () => {
            click_sfx.play();
        });
    });

    // Check if the user has already agreed to the privacy policy from cookies set as "privacy-agreement"
    const hasAgreed =
        document.cookie
            .split("; ")
            .find((row) => row.startsWith("privacy_agreed="))
            ?.split("=")[1] === "true";

    if (window.location.pathname !== "/modal_privacy_policy" && !hasAgreed) {
        // Create the modal
        const modal = document.createElement("div");
        modal.id = "privacy-modal";
        modal.style.position = "fixed";
        modal.style.top = "0";
        modal.style.left = "0";
        modal.style.width = "100%";
        modal.style.height = "100%";
        modal.style.backgroundColor = "rgba(0, 0, 0, 0.5)";
        modal.style.display = "flex";
        modal.style.justifyContent = "center";
        modal.style.alignItems = "center";
        modal.style.zIndex = "1000";

        modal.innerHTML = `
            <div style="background: white; padding: 20px; border-radius: 8px; text-align: center; max-width: 400px; width: 100%;">
                <h2>Privacy Policy</h2>
                <iframe src="/modal_privacy_policy" style="width: 100%; height: 300px; border: 1px solid #ccc; margin-top: 10px; border-radius: 4px;" scrolling="yes"></iframe>
                <button id="agree-btn" style="margin-top: 10px;" class="btn">I Agree</button>
            </div>
        `;

        document.body.appendChild(modal);

        const agreeButton = document.getElementById("agree-btn");
        agreeButton.addEventListener("click", () => {
            // Post agreement
            fetch("/privacy-agreement", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ agreed: true }),
            })
                .then((response) => {
                    if (response.ok) {
                        modal.style.display = "none"; // Hide the modal
                    } else {
                        alert("Failed to submit agreement.");
                    }
                })
                .catch((error) => {
                    console.error("Error:", error);
                    alert("An error occurred.");
                });
        });
    }
});
