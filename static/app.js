// ========================================
// Global state
// ========================================
let token = null;
let loginPromise = null;


// ========================================
// Page init
// ========================================
window.onload = async function () {
    disableInput(true);

    loginPromise = ensureLogin();
    await loginPromise;

    if (token) {
        await loadHistory();
    }

    disableInput(false);
};


// ========================================
// Disable / Enable input
// ========================================
function disableInput(disabled) {
    const input = document.getElementById("input");
    const button = document.querySelector("button");

    if (input) input.disabled = disabled;
    if (button) button.disabled = disabled;
}


// ========================================
// Ensure login (JWT)
// ========================================
async function ensureLogin() {

    const savedToken = localStorage.getItem("token");

    if (savedToken) {
        token = savedToken;
        return;
    }

    try {
        const response = await fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: "alan"
            })
        });

        if (!response.ok) {
            console.error("Login failed");
            return;
        }

        const data = await response.json();
        token = data.access_token;

        localStorage.setItem("token", token);

        console.log("Login successful");

    } catch (err) {
        console.error("Login error:", err);
    }
}


// ========================================
// Load history from backend
// ========================================
async function loadHistory() {

    try {
        const response = await fetch("/history", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        if (!response.ok) {
            console.error("Failed to load history");
            return;
        }

        const history = await response.json();
        const messages = document.getElementById("messages");

        messages.innerHTML = "";

        history.forEach(msg => {
            const div = document.createElement("div");
            div.className = "message " + msg.role;
            div.innerText = msg.content;
            messages.appendChild(div);
        });

        messages.scrollTop = messages.scrollHeight;

    } catch (err) {
        console.error("History load error:", err);
    }
}


// ========================================
// Reset chat
// ========================================
async function resetChat() {

    if (!token) return;

    try {
        await fetch("/reset", {
            method: "POST",
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        document.getElementById("messages").innerHTML = "";

    } catch (err) {
        console.error("Reset error:", err);
    }
}


// ========================================
// Send message
// ========================================
async function send() {

    if (loginPromise) {
        await loginPromise;
    }

    if (!token) {
        alert("Login failed. Please refresh.");
        return;
    }

    const input = document.getElementById("input");
    const messages = document.getElementById("messages");

    const text = input.value.trim();
    if (!text) return;

    // ---------- user message ----------
    const userDiv = document.createElement("div");
    userDiv.className = "message user";
    userDiv.innerText = text;
    messages.appendChild(userDiv);

    input.value = "";
    messages.scrollTop = messages.scrollHeight;

    // ---------- bot message container ----------
    const botDiv = document.createElement("div");
    botDiv.className = "message bot";
    messages.appendChild(botDiv);
    messages.scrollTop = messages.scrollHeight;

    try {

        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify({
                message: text
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            botDiv.innerText = "Server error: " + errorText;
            return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        let fullText = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            fullText += chunk;

            botDiv.innerText = fullText;
            messages.scrollTop = messages.scrollHeight;
        }

    } catch (err) {
        console.error("Connection error:", err);
        botDiv.innerText = "Connection error.";
    }
}


// ========================================
// Press Enter to send
// ========================================
document.getElementById("input")
    .addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            send();
        }
    });

window.send = send;
window.resetChat = resetChat;