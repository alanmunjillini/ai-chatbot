async function send() {
    const input = document.getElementById("input");
    const messages = document.getElementById("messages");

    const text = input.value.trim();
    if (!text) return;

    // user message
    const userDiv = document.createElement("div");
    userDiv.className = "message user";
    userDiv.innerText = text;
    messages.appendChild(userDiv);

    input.value = "";
    messages.scrollTop = messages.scrollHeight;

    // bot message container
    const botDiv = document.createElement("div");
    botDiv.className = "message bot";
    messages.appendChild(botDiv);
    messages.scrollTop = messages.scrollHeight;

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text })
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            botDiv.innerText += chunk;
            messages.scrollTop = messages.scrollHeight;
        }

    } catch (err) {
        botDiv.innerText = "Connection error.";
    }
}

document.getElementById("input")
    .addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
            send();
        }
    });