document.addEventListener("DOMContentLoaded", () => {
  const toggleBtn = document.getElementById("raya-toggle");
  const box = document.getElementById("raya-box");
  const sendBtn = document.getElementById("raya-send");
  const input = document.getElementById("raya-input");
  const messages = document.getElementById("raya-messages");

  toggleBtn.addEventListener("click", () => {
    box.style.display = box.style.display === "block" ? "none" : "block";
  });

  function addMessage(text, sender) {
    const msg = document.createElement("div");
    msg.textContent = `${sender}: ${text}`;
    messages.appendChild(msg);
    messages.scrollTop = messages.scrollHeight;
  }

  sendBtn.addEventListener("click", () => {
    const query = input.value.trim();
    if (!query) return;
    addMessage(query, "You");
    input.value = "";

    // Simulate Raya’s AI response
    setTimeout(() => {
      addMessage("Processing... 🤖", "Raya");
    }, 600);
  });
});