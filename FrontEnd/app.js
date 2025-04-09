
const API_BASE = "https://a438-2a01-4f8-c17-eb2e-00-1.ngrok-free.app";


// Session-Check Funktion
async function checkSession(username) {
    try {
        const res = await fetch(`${API_BASE}/check_session?username=${username}`);
        const data = await res.json();

        if (!data.exists) {
            // Keine Session gefunden → Weiterleitung zur Onboarding-Seite
            window.location.href = "https://teal-cheesecake-9a0880.netlify.app"; // Deine Onboarding-Seite
        }
    } catch (error) {
        console.error("❌ Fehler beim Session Check:", error);
    }
}

let sessionId = localStorage.getItem("session_id") || "";

// Status Anzeige
function setStatus(msg, isError = false) {
    const status = document.getElementById("status");
    status.style.color = isError ? "red" : "green";
    status.innerText = msg;
}

// Login-Funktion
async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
        // Session prüfen
        const sessionCheck = await fetch(`${API_BASE}/check_session?username=${username}`);
        const sessionData = await sessionCheck.json();

        if (!sessionData.exists) {
            // Weiterleitung zur Onboarding-Seite, wenn keine Session existiert
            window.location.href = "https://teal-cheesecake-9a0880.netlify.app";
            return;
        }

        // Login API Request
        const res = await fetch(`${API_BASE}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        const data = await res.json();

        if (data.session_id) {
            sessionId = data.session_id;
            localStorage.setItem("session_id", sessionId);

            if (data.registered) {
                setStatus("✅ Session gefunden. Nachrichten können geladen werden.");
            } else {
                setStatus("🔐 Neue Session nötig – bitte TikTok Login abschließen.");
            }
        } else {
            setStatus("❌ Login fehlgeschlagen!", true);
        }
    } catch (error) {
        console.error("❌ Fehler beim Login:", error);
        setStatus("❌ Serverfehler – bitte später erneut versuchen.", true);
    }
}

// Nachrichten abrufen
async function fetchMessages() {
    if (!sessionId) {
        return setStatus("⚠️ Bitte zuerst einloggen!", true);
    }

    setStatus("⏳ Lade Nachrichten...");

    try {
        const res = await fetch(`${API_BASE}/fetch_messages?session_id=${sessionId}`, {
            method: "POST"
        });

        const data = await res.json();
        console.log("📦 Nachrichten vom Server:", data);

        const container = document.getElementById("messages");
        container.innerHTML = "";

        if (!data || !data.length) {
            container.innerHTML = "<p>Keine Nachrichten gefunden.</p>";
            return setStatus("ℹ️ Abruf abgeschlossen – aber keine Nachrichten.");
        }

        data.forEach(msg => {
            const div = document.createElement("div");
            div.classList.add("msg");
            div.innerHTML = `
                <strong>From:</strong> ${msg.sender} <br/>
                <strong>Message:</strong> ${msg.content} <br/>
                <small>${msg.timestamp}</small>
            `;
            container.appendChild(div);
        });

        setStatus(`✅ ${data.length} Nachrichten geladen.`);
    } catch (e) {
        console.error("❌ Fehler beim Abrufen der Nachrichten:", e);
        setStatus("❌ Serverfehler – bitte später erneut versuchen", true);
    }
}

