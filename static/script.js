document.addEventListener("DOMContentLoaded", async function () {
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

        const content = await fetch("/modal_privacy_policy", {
            method: "POST",
        })
            .then((response) => response.json())
            .then((data) => data);
        const backgroundColor = document.documentElement.getAttribute("data-bs-theme");

        modal.innerHTML = `
            <div class="p-4 rounded text-center bg-${backgroundColor}" style="max-width: 400px; width: 100%;">
            <h2>Cookies and Privacy Policy</h2>
            <div class="w-100 overflow-auto border mt-2 rounded" style="height: 300px;">
                ${content[1]}
            </div>
            <button id="agree-btn" class="btn btn-primary mt-3">I Agree</button>
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

    const theme = document.cookie.split("; ").find((row) => row.startsWith("theme="));
    if (theme) {
        const currentThemeValue = document.documentElement.getAttribute("data-bs-theme");
        const themeValue = theme.split("=")[1];
        if (currentThemeValue !== themeValue) {
            document.documentElement.setAttribute("data-bs-theme", themeValue);
            fetch("/set_theme", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ theme: themeValue }),
            }).catch((error) => {
                console.error("Error setting theme:", error);
            });
        }
    } else {
        const currentThemeValue = document.documentElement.getAttribute("data-bs-theme");
        if (currentThemeValue !== "dark" && currentThemeValue !== "light") {
            document.documentElement.setAttribute("data-bs-theme", "light");
            fetch("/set_theme", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ theme: "light" }),
            }).catch((error) => {
                console.error("Error setting theme:", error);
            });
            return;
        }
        document.cookie = `theme=${currentThemeValue}; path=/; max-age=${30 * 24 * 60 * 60}; SameSite=Strict; Secure`;
    }
});
