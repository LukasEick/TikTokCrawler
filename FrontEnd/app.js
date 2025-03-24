let session_id = "";

async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const response = await fetch("https://your-render-url.com/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    });

    const data = await response.json();
    session_id = data.session_id;
    alert("Logged in successfully!");
}

async function fetchMessages() {
    const response = await fetch(`https://your-render-url.com/fetch_messages?session_id=${session_id}`, {
        method: "POST"
    });

    const data = await response.json();
    const container = document.getElementById("messages");
    container.innerHTML = "";
    data.messages.forEach(msg => {
        container.innerHTML += `<p><strong>${msg.sender}:</strong> ${msg.content} <br><em>${msg.timestamp}</em></p>`;
    });
}
