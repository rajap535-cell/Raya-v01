document.addEventListener("DOMContentLoaded", () => {
  fetch("../data/experiments.json")
    .then((response) => response.json())
    .then((data) => {
      const container = document.getElementById("experiments-container");

      data.forEach((exp) => {
        const card = document.createElement("div");
        card.className = "planet-card";

        card.innerHTML = `
          <div class="flex items-center gap-3 mb-3">
            <span class="text-3xl">${exp.icon || "✨"}</span>
            <h2 class="planet-title">${exp.title}</h2>
          </div>
          <p class="planet-desc mb-4">${exp.description}</p>
          <div class="flex items-center justify-between">
            ${exp.category ? `<span class="text-xs px-2 py-1 bg-indigo-900/10 text-indigo-600 rounded-full font-medium">${exp.category}</span>` : ""}
            <a href="${exp.link}" class="text-cyan-600 hover:text-cyan-400 text-sm font-bold transition-colors">Launch →</a>
          </div>
        `;

        container.appendChild(card);
      });
    })
    .catch((error) => {
      console.error("Error loading experiments:", error);
    });
});
