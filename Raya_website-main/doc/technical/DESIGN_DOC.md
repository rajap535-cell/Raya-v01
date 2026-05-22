# RAYA Website Design Document (TL;DR)

## 🌌 Overview

**RAYA** is a digital interface for the **Planetary Coordination Architecture**. The website serves as a knowledge hub and vision portal for India's indigenous AI ecosystem, aiming to transition humanity toward a **Type-I Civilization**.

---

## 🏗️ Architecture & Development

The site is built as a **Modular Static Site** using vanilla technologies for maximum performance and auditability.

- **Modular Loading**: Uses a custom `layout-loader.js` (Fetch API) to inject shared components like the Navbar, Footer, and Raya Assistant. It includes post-fetch initialization logic for interactive elements like mobile menus and scroll listeners.
- **Path Management**: Automated path normalization ensures components work seamlessly whether accessed from the `root` or deep within the `/public` directory.
- **Sticky Navigation**: Implements a `sticky` positioning system that keeps the primary navigation accessible while maintaining a clean layout, especially below deep scrolly hero sections.

---

## 🎨 Design System

The visual language reflects a "Planetary Intelligence" theme, combining scientific clarity with futuristic aesthetics.

### 💎 Aesthetics

- **Glassmorphism**: UI cards and the sticky navigation bar use `backdrop-filter: blur()` and semi-transparent gradients for a layered, futuristic feel.
- **Dynamic Motion**: Subtle `floaty` keyframe animations and hover-based scaling on interactive elements.
- **Mobile Accessibility**: Includes a responsive hamburger menu with keyboard support (ESC key closure and tab focus focusability).
- **Color Palette**:
  - `--aqua` (#00E6FF): Primary accent for technology and energy.
  - `--deep` (#13397b): Foundation color for structure and text.
  - `--gold` (#FFD369): Secondary accent for insights and "runic" elements.

---

## 🛠️ Technology Stack

- **Structure**: Semantic HTML5.
- **Styling**: **Tailwind CSS 4.0** (Browser-side CDN) + Custom Vanilla CSS for specialized animations and gradients.
- **Logic**: Vanilla JavaScript (ES6+), focusing on DOM manipulation and asynchronous component loading.

---

## 🗺️ Key Features & Pages

1.  **Planetary Pillars**: Interactive cards on the landing page describing Raya’s research into Energy, Water, Farming, and Human Sustainability.
2.  **Vision Portal**: A comprehensive breakdown of the "Why" behind the project (`vision_main.html`).
3.  **Journey Tracker**: A roadmap detailing milestones from 2025 to 2026 (`journey.html`).
4.  **Integrated Navigation**: A globally consistent, responsive navigation menu sitting below scrolly animations on the home page and sticky across all subpages.
5.  **Raya Assistant**: A floating modular component that provides context-aware guidance across the site.

---

## 📂 Project Structure

```bash
├── assets/             # Visual assets (Planetary imagery, logos)
├── data/               # Research and data sources
├── doc/                # Whitepapers and presentations
├── public/             # Modular sub-pages (Mission-specific content)
├── src/
│   ├── components/     # Reusable HTML snippets (Navbar, Footer, Assistant)
│   └── scripts/        # Domain logic and layout loaders
├── index.html          # Entry point
└── index.css           # Global design tokens and animations
```
