const chatBox = document.getElementById("chat-box");
const messageInput = document.getElementById("message-input");

const sessionId = "web-user-" + Date.now();

async function sendMessage() {
    const message = messageInput.value.trim();

    if (!message) {
        return;
    }

    addMessage(message, "user");
    messageInput.value = "";

    try {
        const response = await fetch("http://127.0.0.1:8000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                session_id: sessionId,
                message: message
            })
        });

        const data = await response.json();

        if (response.ok) {
            addMessage(data.response, "bot");
        } else {
            addMessage("Sorry, something went wrong.", "bot");
        }

    } catch (error) {
        addMessage(
            "Could not connect to the LeadPilot server. Make sure FastAPI is running.",
            "bot"
        );
    }
}

function addMessage(text, type) {
    const messageDiv = document.createElement("div");

    messageDiv.className = `message ${type}`;
    messageDiv.textContent = text;

    chatBox.appendChild(messageDiv);

    chatBox.scrollTop = chatBox.scrollHeight;
}

messageInput.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});