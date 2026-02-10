async function loadUpdates() {
  try {
    const response = await fetch("updates.json");
    const updates = await response.json();
    const container = document.getElementById("updates-container");

    updates.forEach(update => {
      const card = document.createElement("div");
      card.className =
        "p-6 rounded-xl border border-yellow-400 shadow-lg shadow-yellow-400/30 bg-slate-950/60 hover:shadow-yellow-400/60 hover:scale-105 transition transform";

      card.innerHTML = `
        <p class="text-yellow-300 text-sm mb-2">${update.date}</p>
        <h3 class="text-xl font-bold text-cyan-300 mb-3">${update.title}</h3>
        <p class="text-slate-300">${update.summary}</p>
      `;

      container.appendChild(card);
    });
  } catch (error) {
    console.error("Failed to load updates:", error);
  }
}

document.addEventListener("DOMContentLoaded", loadUpdates);