let conversationId = null;

function startNewConversation() {
  conversationId = null;
  document.getElementById("chat-window").innerHTML = "";
}

function toggleSidebar() {
  document.getElementById("sidebar").classList.toggle("open");
  document.getElementById("sidebar-backdrop").classList.toggle("open");
}

async function sendMessage() {
  const input = document.getElementById("msg-input");
  const chatWindow = document.getElementById("chat-window");
  const message = input.value.trim();
  if (!message) return;

  chatWindow.innerHTML += `
    <div class="bubble-row user">
      <div class="bubble-user">${message}</div>
    </div>`;
  input.value = "";
  chatWindow.scrollTop = chatWindow.scrollHeight;

  const response = await fetch("/api/chat/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: message, conversation_id: conversationId }),
  });
  const data = await response.json();
  conversationId = data.conversation_id;

  chatWindow.innerHTML += `
    <div class="bubble-row bot">
      <div class="bot-message">
        <div class="bot-label">ASSISTANT</div>
        <div class="bubble-bot">${data.answer}</div>
      </div>
    </div>`;
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

document.getElementById("msg-input").addEventListener("keypress", function (e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});