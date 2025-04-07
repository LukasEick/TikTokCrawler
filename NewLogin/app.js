async function startOnboarding() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    setStatus("🚀 Starte Onboarding...");

    try {
        const res = await fetch("https://tiktokcrawler-1.onrender.com/onboarding", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        const data = await res.json();

        if (data.session_id) {
            setStatus("✅ Session erfolgreich erstellt!");
            // Optional weiterleiten
            setTimeout(() => {
                window.location.href = "https://deine-hauptseite.netlify.app";
            }, 2000);
        } else {
            setStatus("❌ Fehler beim Erstellen der Session!", true);
        }
    } catch (error) {
        console.error(error);
        setStatus("❌ Fehler beim Onboarding", true);
    }
}
