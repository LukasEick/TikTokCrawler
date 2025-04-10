const API_BASE = "https://lukastest.duckdns.org";

let sessionId = localStorage.getItem("session_id") || "";

// DOM Elemente
const fetchButton = document.getElementById("fetchButton");
const statusElement = document.getElementById("status");

// Anfang: Fetch Button deaktivieren
if (fetchButton) fetchButton.disabled = true;

// Status Anzeige
function setStatus(msg, isError = false) {
    statusElement.style.color = isError ? "red" : "green";
    statusElement.innerText = msg;
}

// Session-Check Funktion
async function checkSession(username) {
    try {
        const res = await fetch(`${API_BASE}/check_session?username=${username}`);
        const data = await res.json();

        if (!data.exists) {
            window.location.href = "https://precious-rolypoly-9d9b00.netlify.app";
        }
    } catch (error) {
        console.error("❌ Fehler beim Session Check:", error);
    }
}

// Login-Funktion
async function login() {
    const username = document.getElementById("username").value.trim().toLowerCase().replace(" ", "_");
    const password = document.getElementById("password").value;

    if (!username || !password) {
        return setStatus("❌ Bitte Username und Passwort eingeben!", true);
    }

    setStatus("🔐 Überprüfe Login...");

    try {
        const sessionCheck = await fetch(`${API_BASE}/check_session?username=${username}`);
        const sessionData = await sessionCheck.json();

        if (!sessionData.exists) {
            window.location.href = "https://precious-rolypoly-9d9b00.netlify.app";
            return;
        }

        const res = await fetch(`${API_BASE}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        const data = await res.json();

        if (data.session_id) {
            sessionId = data.session_id;
            localStorage.setItem("session_id", sessionId);

            setStatus("✅ Erfolgreich eingeloggt!");
            if (fetchButton) fetchButton.disabled = false;

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
