let sessionId = localStorage.getItem("session_id") || "";

function setStatus(msg, isError = false) {
    const status = document.getElementById("status");
    status.style.color = isError ? "red" : "green";
    status.innerText = msg;
}

async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const res = await fetch("https://tiktokcrawler-1.onrender.com/login", {
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
}

async function fetchMessages() {
    if (!sessionId) {
        return setStatus("⚠️ Bitte zuerst einloggen!", true);
    }

    setStatus("⏳ Lade Nachrichten...");

    let data;
    try {
        const res = await fetch(`https://tiktokcrawler-1.onrender.com/fetch_messages?session_id=${sessionId}`, {
            method: "POST"
        });

        data = await res.json();
        console.log("📦 Nachrichten vom Server:", data);

    } catch (e) {
        console.error("❌ Fehler beim Abrufen der Nachrichten:", e);
        setStatus("❌ Serverfehler – bitte später erneut versuchen", true);
        return;
    }

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
}



