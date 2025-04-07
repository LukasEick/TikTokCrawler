async function startOnboarding() {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();

    if (!username || !password) {
        alert("Bitte fülle alle Felder aus.");
        return;
    }

    document.getElementById('status').innerText = "🚀 Starte Session Erstellung, bitte warten...";

    try {
        const res = await fetch('https://tiktokcrawler-1.onrender.com/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (!res.ok) {
            throw new Error("Fehler beim Erstellen der Session.");
        }

        document.getElementById('status').innerText = "✅ Session erfolgreich erstellt! Weiterleitung...";

        // Kleine Verzögerung für UX
        setTimeout(() => {
            window.location.href = "/"; // Zur Hauptseite
        }, 2000);

    } catch (error) {
        console.error(error);
        document.getElementById('status').innerText = "❌ Fehler: " + error.message;
    }
}
