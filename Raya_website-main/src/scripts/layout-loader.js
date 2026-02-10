/**
 * layout-loader.js
 * Utility to load shared layout components (Navbar, Footer, etc.)
 */

// Global System Configuration
const SYSTEM_CONFIG = {
  ENV: 'DEV', // Options: DEV, QA, UAT, PROD
  BUILD: {
    VERSION: '1.2.4',
    NUMBER: '852'
  }
};

function initializeNavbar() {
  const toggle = document.getElementById('mobile-toggle');
  const menu = document.getElementById('mobile-menu');
  const navContainer = document.querySelector('.nav-container');

  if (!toggle || !menu) return;

  // Toggle Menu
  toggle.addEventListener('click', (e) => {
    e.stopPropagation();
    const isActive = menu.classList.toggle('active');
    toggle.classList.toggle('active');
    toggle.setAttribute('aria-expanded', isActive);
  });

  // Close on Outside Click
  document.addEventListener('click', (e) => {
    if (menu.classList.contains('active') && !menu.contains(e.target) && !toggle.contains(e.target)) {
      menu.classList.remove('active');
      toggle.classList.remove('active');
      toggle.setAttribute('aria-expanded', 'false');
    }
  });

  // Close on ESC
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && menu.classList.contains('active')) {
      menu.classList.remove('active');
      toggle.classList.remove('active');
      toggle.setAttribute('aria-expanded', 'false');
    }
  });

  // Scroll Behavior
  window.addEventListener('scroll', () => {
    if (window.scrollY > 20) {
      navContainer.classList.add('scrolled');
    } else {
      navContainer.classList.remove('scrolled');
    }
  });
}

function loadLayout() {
  const elements = {
    'navbar-placeholder': 'src/components/navbar.html',
    'footer-placeholder': 'src/components/footer.html',
    'vision-nav-placeholder': 'src/components/vision-nav.html',
    'raya-assistant-container': 'src/components/raya-assistant.html'
  };

  // Robust path resolution: Find how many steps we are from the root
  // We assume 'src' is at the root.
  const pathParts = window.location.pathname.split('/');
  // Filter out empty strings from leading/trailing slashes
  const cleanParts = pathParts.filter(p => p.length > 0);
  
  // Find the index of 'public' or if we are at root
  const publicIndex = cleanParts.indexOf('public');
  let prefix = '';
  
  if (publicIndex !== -1) {
    // Number of steps from 'public' to the end of the path
    const depth = cleanParts.length - 1 - publicIndex;
    // We need to go up 'depth + 1' to reach root (where src/ is)
    prefix = '../'.repeat(depth + 1);
  }

  const isPublic = publicIndex !== -1;

  const promises = Object.entries(elements).map(([id, path]) => {
    const container = document.getElementById(id);
    if (!container) return Promise.resolve();

    return fetch(prefix + path)
      .then(res => res.text())
      .then(html => {
        // Adjust paths inside the loaded HTML
        if (isPublic) {
          if (id !== 'vision-nav-placeholder') {
            html = html.replace(/href="public\//g, 'href="' + prefix + 'public/');
            html = html.replace(/href="index.html"/g, 'href="' + prefix + 'index.html"');
            html = html.replace(/src="assets\//g, 'src="' + prefix + 'assets/');
          }
        }
        
        container.innerHTML = html;

        // Execute any <script> tags in the loaded content
        const scripts = container.querySelectorAll("script");
        scripts.forEach(oldScript => {
          const newScript = document.createElement("script");
          if (oldScript.src) {
            newScript.src = oldScript.src;
          } else {
            newScript.textContent = oldScript.textContent;
          }
          document.body.appendChild(newScript);
          oldScript.remove();
        });

        if (id === 'footer-placeholder') {
          const envEl = document.getElementById('env-label');
          const buildEl = document.getElementById('build-label');
          if (envEl) envEl.textContent = SYSTEM_CONFIG.ENV;
          if (buildEl) buildEl.textContent = `v${SYSTEM_CONFIG.BUILD.VERSION}-b${SYSTEM_CONFIG.BUILD.NUMBER}`;
        }
      })
      .catch(err => console.error(`Failed to load component ${id}:`, err));
  });

  Promise.all(promises).then(() => {
    initializeNavbar();
  });
}

document.addEventListener('DOMContentLoaded', loadLayout);
