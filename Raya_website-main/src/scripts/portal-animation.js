/**
 * Raya Neural Eye Portal Animation
 * A generative webgl-like 2D canvas animation for Raya's Type I core interaction.
 */

class PortalAnimation {
    constructor() {
        this.canvas = document.getElementById('portal-canvas');
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        this.time = 0;
        this.mouse = { x: 0, y: 0 };
        this.particles = [];
        this.rings = 4;
        
        this.init();
    }

    init() {
        window.addEventListener('resize', () => this.resize());
        window.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        
        // Wait for layout to settle
        requestAnimationFrame(() => {
            this.resize();
            this.animate();
        });

        // Initial setup for nodes
        for(let i=0; i<40; i++) {
            this.particles.push({
                angle: Math.random() * Math.PI * 2,
                dist: 80 + Math.random() * 120,
                size: 1 + Math.random() * 2,
                speed: 0.002 + Math.random() * 0.005,
                pulse: Math.random() * Math.PI
            });
        }

        this.animate();
    }

    resize() {
        if (!this.canvas || !this.canvas.parentElement) return;
        
        const parent = this.canvas.parentElement;
        const dpr = window.devicePixelRatio || 1;
        const rect = parent.getBoundingClientRect();
        
        // CSS dimensions
        this.width = rect.width;
        this.height = rect.height;
        
        // Canvas resolution
        this.canvas.width = this.width * dpr;
        this.canvas.height = this.height * dpr;
        
        // Normalize coordinate system
        this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    handleMouseMove(e) {
        const rect = this.canvas.getBoundingClientRect();
        this.mouse.x = (e.clientX - (rect.left + rect.width / 2)) / (rect.width / 2);
        this.mouse.y = (e.clientY - (rect.top + rect.height / 2)) / (rect.height / 2);
    }

    animate() {
        this.time += 0.01;
        this.draw();
        requestAnimationFrame(() => this.animate());
    }

    draw() {
        const { width, height } = this;
        this.ctx.clearRect(0, 0, width, height);
        
        const centerX = width / 2;
        const centerY = height / 2;
        const baseRadius = Math.min(width, height) * 0.18;

        // Apply mouse-based parallax
        const tiltX = this.mouse.x * 20;
        const tiltY = this.mouse.y * 20;

        // Draw Rings
        for(let i=1; i<=this.rings; i++) {
            const r = baseRadius * (1 + i * 0.3);
            const rotation = this.time * (i % 2 === 0 ? 0.2 : -0.2);
            
            this.ctx.strokeStyle = `rgba(34, 211, 238, ${0.1 / i})`;
            this.ctx.lineWidth = 1;
            
            this.ctx.beginPath();
            this.ctx.ellipse(
                centerX + tiltX * (i/2), 
                centerY + tiltY * (i/2), 
                r, 
                r * 0.8, 
                rotation, 
                0, 
                Math.PI * 2
            );
            this.ctx.stroke();

            // Ring sensor dots
            if (i > 1) {
                const dotAngle = rotation * 2 + (i * Math.PI/2);
                const dx = centerX + tiltX * (i/2) + Math.cos(dotAngle) * r;
                const dy = centerY + tiltY * (i/2) + Math.sin(dotAngle) * (r * 0.8);
                
                this.ctx.fillStyle = `rgba(34, 211, 238, ${0.4})`;
                this.ctx.beginPath();
                this.ctx.arc(dx, dy, 2, 0, Math.PI * 2);
                this.ctx.fill();
                
                // Connection line to center
                this.ctx.strokeStyle = `rgba(34, 211, 238, ${0.05})`;
                this.ctx.beginPath();
                this.ctx.moveTo(dx, dy);
                this.ctx.lineTo(centerX, centerY);
                this.ctx.stroke();
            }
        }

        // Draw Main Eye Glow
        const gradient = this.ctx.createRadialGradient(
            centerX + tiltX, centerY + tiltY, 0,
            centerX + tiltX, centerY + tiltY, baseRadius
        );
        gradient.addColorStop(0, 'rgba(34, 211, 238, 0.4)');
        gradient.addColorStop(0.5, 'rgba(34, 211, 238, 0.1)');
        gradient.addColorStop(1, 'transparent');
        
        this.ctx.fillStyle = gradient;
        this.ctx.beginPath();
        this.ctx.arc(centerX + tiltX, centerY + tiltY, baseRadius, 0, Math.PI * 2);
        this.ctx.fill();

        // Particles
        this.particles.forEach(p => {
            p.angle += p.speed;
            p.pulse += 0.05;
            
            const px = centerX + Math.cos(p.angle) * p.dist + tiltX * 1.5;
            const py = centerY + Math.sin(p.angle) * (p.dist * 0.8) + tiltY * 1.5;
            const size = p.size * (1 + Math.sin(p.pulse) * 0.5);

            this.ctx.fillStyle = `rgba(34, 211, 238, ${0.2 + (1 - p.dist/250)})`;
            this.ctx.beginPath();
            this.ctx.arc(px, py, size, 0, Math.PI * 2);
            this.ctx.fill();
        });

        // Core Pulse
        const coreSize = 10 + Math.sin(this.time * 2) * 5;
        this.ctx.shadowBlur = 20;
        this.ctx.shadowColor = 'rgba(34, 211, 238, 0.8)';
        this.ctx.fillStyle = '#fff';
        this.ctx.beginPath();
        this.ctx.arc(centerX + tiltX, centerY + tiltY, coreSize, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.shadowBlur = 0;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new PortalAnimation();
});
