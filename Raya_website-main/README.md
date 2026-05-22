# RAYA — Open Knowledge Intelligence

## 🚀

See the [Design Doc](doc/DESIGN_DOC.md) for architectural details.

**RAYA** is an open-source, community-first initiative building a **Planetary Coordination Architecture**. It aims to create a transparent, auditable intelligence system to manage Earth's energy, water, and resources, guiding humanity toward a **Type-I Civilization**.

---

## 🌍 Vision

Raya is not just a product; it’s an evolving architecture for planetary-scale intelligence. It bridges the gap between fragmented human coordination and the unified nature of Earth's physical systems.

### Core Pillars

- **Open Intelligence:** Auditable models and public development logs.
- **Planetary Coordination:** Managing energy, water, and food systems.
- **Type-I Civilization:** Transitioning from information systems to global planetary intelligence.
- **Foundational Principles:** Long-term stability, scientific integrity, and planetary limits.

## 📁 Project Structure

```bash
├── assets/             # Branding, icons, and planetary theme imagery
├── data/               # Project data and research files
├── doc/                # Strategic vision docs, presentations, and [Design Doc](doc/DESIGN_DOC.md)
├── public/             # Main site pages (Vision, Journey, Portal, etc.)
├── src/
│   └── components/     # Reusable UI components (e.g., Raya Assistant)
├── index.html          # Primary landing page
└── index.css           # Global styles and design system tokens
```

## 🛠️ Technology Stack

- **Structure:** Semantic HTML5
- **Styling:** Tailwind CSS 4.0 (CDN-based) & Vanilla CSS
- **Interactivity:** Vanilla JavaScript (ES6+)
- **Components:** Modular HTML fetching system

## 🚦 Getting Started

Since the website uses the `Fetch API` to load modular components (like the Raya Assistant), it requires a local server to run correctly (to avoid CORS issues).

### Recommended Ways to View:

1. **VS Code Live Server:** Right-click `index.html` and select "Open with Live Server".
2. **Python:** Run `python -m http.server` in the root directory.
3. **Node.js:** Run `npx serve .`

## 🗺️ Navigation Guide

- **Home:** [index.html](index.html) — Back to the start.
- **Vision:** [public/vision_main.html](public/vision_main.html) — The "Why" behind Raya.
- **Journey:** [public/journey.html](public/journey.html) — Roadmap and milestones for 2025–2026.
- **Experiments:** [public/old/experiments.html](public/old/experiments.html) — Interactive demos and prototypes.
- **Portal Login:** [public/portal_login.html](public/portal_login.html) — Secure gateway to the technical system.
- **Energy Dashboard:** [public/dashboard.html](public/dashboard.html) — (Auth Required) Live energy optimization and predictive modeling interface.
- **Challenges:** [public/raya_problem.html](public/raya_problem.html) — Global coordination failures Raya aims to solve.

---

## ⚡ Operational Modules

### Energy Intelligence (RJ-204)
A deterministic optimization layer for industrial and distributed energy systems. 
- **Live Monitoring:** Real-time telemetry indexing of regional demand vs. temperature trends.
- **Prediction Engine:** Random Forest (v0.1) based simulation for multi-variate load forecasting.
- **Deterministic Logic:** Ensuring auditable, policy-bound system actions.

---

_“From Darkness to Light — tamso mā jyotirgamaya”_
