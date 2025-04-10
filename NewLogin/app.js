function setStatus(message, isError = false) {
    const statusElement = document.getElementById("status");
    if (!statusElement) return;

    statusElement.textContent = message;
    statusElement.style.color = isError ? "red" : "green";

    statusElement.style.opacity = "1";
    setTimeout(() => {
        statusElement.style.opacity = "0.8";
    }, 3000);
}

async function startOnboarding() {
    const username = document.getElementById("username").value.trim().toLowerCase().replace(" ", "_");
    const password = document.getElementById("password").value;

    if (!username || !password) {
        setStatus("❌ Bitte Username und Passwort eingeben!", true);
        return;
    }

    setStatus("🚀 Starte Onboarding...");

    try {
        const res = await fetch("https://00c1-2a01-4f8-c17-eb2e-00-1.ngrok-free.app/onboarding", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        if (!res.ok) {
            throw new Error("Server antwortete mit Fehler");
        }

        const data = await res.json();

        if (data.session_id) {
            setStatus("✅ Session erfolgreich erstellt!");

            // ✅ Optional: Automatische Weiterleitung zur Hauptseite
            setTimeout(() => {
                window.location.href = "https://serene-biscuit-c4a067.netlify.app"; // Deine Hauptseite!
            }, 2000);
        } else {
            setStatus("❌ Session-Erstellung fehlgeschlagen!", true);
        }
    } catch (error) {
        console.error("❌ Fehler beim Onboarding:", error);
        setStatus("❌ Fehler beim Onboarding – bitte später erneut versuchen.", true);
    }
}
