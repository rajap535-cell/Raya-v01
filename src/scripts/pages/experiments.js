document.addEventListener("DOMContentLoaded", () => {
  fetch("experiments.json")
    .then(response => response.json())
    .then(data => {
      const container = document.getElementById("experiments-container");

      data.forEach(exp => {
        const card = document.createElement("div");
        card.className =
          "bg-gray-800 rounded-2xl shadow-lg p-6 transform hover:-translate-y-2 hover:shadow-2xl transition-all duration-300";

        card.innerHTML = `
          <div class="flex items-center gap-3 mb-3">
            <span class="text-3xl">${exp.icon || "✨"}</span>
            <h2 class="text-xl font-bold text-indigo-300">${exp.title}</h2>
          </div>
          <p class="text-gray-300 text-sm mb-4">${exp.description}</p>
          <div class="flex items-center justify-between">
            ${exp.category ? `<span class="text-xs px-2 py-1 bg-indigo-900 text-indigo-300 rounded-full">${exp.category}</span>` : ""}
            <a href="${exp.link}" class="text-indigo-400 hover:text-indigo-200 text-sm font-medium">Try →</a>
          </div>
        `;

        container.appendChild(card);
      });
    })
    .catch(error => {
      console.error("Error loading experiments:", error);
    });
});