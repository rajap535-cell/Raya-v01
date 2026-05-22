# Architecture and Structuring Review: Raya Website

## System Overview & Insights
The RAYA website is currently built as a **Vanilla HTML/CSS/JS** Single-Page-Application (SPA) hybrid. It relies entirely on client-side execution to assemble the interface without the use of a build step, static site generator, or modern frontend framework (like React, Next.js, or Vite).

### Key Insights
1. **Highly Manual Setup:** The architecture relies on browser-native features. You have built a custom component injection system (`layout-loader.js`) to mimic modern frameworks. While this shows great ingenuity, it doesn't scale well for a growing platform.
2. **Performance Bottlenecks:** Heavy lifting (like compiling Tailwind CSS and fetching layout components) is being deferred to the user's browser at runtime. This will negatively impact load times, Core Web Vitals, and SEO.
3. **Pathing Fragility:** Because components are loaded dynamically, your code has to rely on manual string replacements (regex) to fix relative paths for assets and links. This is inherently brittle and prone to breaking as the site structure deepens.

---

## Top 5 Architectural Points That MUST Be Fixed

### 1. **Remove Tailwind CDN & Implement a Build Step**
**The Problem:** In `index.html`, Tailwind is loaded via a browser script (`<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>`). This forces the browser to parse all DOM elements and generate CSS on the fly. It is strictly recommended for development only, not production, as it causes a Flash of Unstyled Content (FOUC) and severe performance degradation.
**The Fix:** Initialize a `package.json` and install Tailwind via NPM. Set up a build script (or use a bundler like Vite) to pre-compile the CSS into a static file before deployment.

### 2. **Replace Client-Side Layout Loading (`layout-loader.js`)**
**The Problem:** Fetching `navbar.html` and `footer.html` asynchronously at runtime via JavaScript and modifying strings with Regex is fragile. It causes layout shifts, hurts SEO (crawlers might not execute the JS to see the navigation), and breaks entirely if a user has a slow connection or disabled JS. 
**The Fix:** Transition to a Static Site Generator (SSG) like **Astro**, **Eleventy**, or a bundler like **Vite** (with HTML partial plugins) to stitch these components together at *build time*, serving complete HTML files to the browser.

### 3. **Restructure the `public/` Directory**
**The Problem:** The `public/` folder is traditionally reserved for static, uncompiled assets that should be served directly at the root (like `favicon.ico`, `robots.txt`, or global images). Currently, you are storing view pages (`dashboard.html`, `hsi_module.html`) and their specific CSS files inside it. This forces awkward relative pathing (e.g., `../public/`).
**The Fix:** Move HTML pages to a dedicated `pages/` or `views/` directory within `src/` (or the root). Reserve `public/` strictly for static static assets that don't require processing.

### 4. **Consolidate and Bundle CSS Assets**
**The Problem:** CSS files are scattered across the project (`index.css` in root, `dashboard.css` in `public/`, `test.css` in `src/styles/`). Loading multiple separate CSS files requires multiple HTTP requests, and there is no minification or tree-shaking happening.
**The Fix:** Move all stylesheets to `src/styles/`. Use a build tool to bundle them into a single, minified `main.css` file for production. This creates a single source of truth for your design tokens.

### 5. **Introduce a Package Manager & Dev Environment**
**The Problem:** The project currently lacks a `package.json`. This means dependencies (like Tailwind, animations, or future libraries) cannot be version-controlled or easily updated. It also means there's no local development server with Hot Module Replacement (HMR).
**The Fix:** Run `npm init -y` to create a package manager. Install a lightweight dev server (like Vite). This will give you instant reloading, automatic asset optimization, and a standardized deployment pipeline (e.g., `npm run build`).
