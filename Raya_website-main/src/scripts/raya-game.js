/**
 * Raya Grid Synchronization Experiment
 * A small interactive game simulating planetary coordination.
 */

class RayaGame {
    constructor() {
        this.canvas = document.getElementById('game-canvas');
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        this.nodes = [];
        this.stability = 100;
        this.score = 0;
        this.isPlaying = false;
        this.maxNodes = 6;
        this.spawnRate = 1500; // ms
        this.lastSpawn = 0;
        this.startTime = 0;

        // Colors
        this.colors = {
            cyan: '#22d3ee',
            red: '#f43f5e',
            bg: '#0a0f1d'
        };

        this.init();
    }

    init() {
        this.resize();
        window.addEventListener('resize', () => this.resize());
        
        const startBtn = document.getElementById('start-game');
        if (startBtn) {
            startBtn.addEventListener('click', () => this.start());
        }
        this.canvas.addEventListener('click', (e) => this.handleClick(e));
        
        // Initial drawing
        this.drawPlaceholder();
    }

    resize() {
        const rect = this.canvas.getBoundingClientRect();
        this.canvas.width = rect.width * window.devicePixelRatio;
        this.canvas.height = rect.height * window.devicePixelRatio;
    }

    start() {
        this.isPlaying = true;
        this.stability = 100;
        this.score = 0;
        this.nodes = [];
        this.startTime = Date.now();
        this.lastSpawn = Date.now();
        
        const overlay = document.getElementById('game-overlay');
        if (overlay) {
            overlay.style.opacity = '0';
            overlay.style.pointerEvents = 'none';
        }
        
        const status = document.getElementById('game-status');
        if (status) status.innerText = 'OPERATIONAL // ACTIVE';
        
        const score = document.getElementById('game-score');
        if (score) score.innerText = '100';
        
        this.loop();
    }

    stop() {
        this.isPlaying = false;
        const overlay = document.getElementById('game-overlay');
        if (overlay) {
            overlay.style.opacity = '1';
            overlay.style.pointerEvents = 'auto';
        }
        
        const status = document.getElementById('game-status');
        if (status) status.innerText = 'SYSTEM FAILURE // STANDBY';
        
        const startBtn = document.getElementById('start-game');
        if (startBtn) startBtn.innerText = 'REINITIALIZE';
    }

    spawnNode() {
        const padding = 50;
        const x = padding + Math.random() * (this.canvas.width - padding * 2);
        const y = padding + Math.random() * (this.canvas.height - padding * 2);
        
        this.nodes.push({
            x, y,
            radius: 20,
            unstability: 0, // 0 to 1
            decayRate: 0.002 + Math.random() * 0.003
        });
    }

    handleClick(e) {
        if (!this.isPlaying) return;

        const rect = this.canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left) * (this.canvas.width / rect.width);
        const y = (e.clientY - rect.top) * (this.canvas.height / rect.height);

        for (let i = this.nodes.length - 1; i >= 0; i--) {
            const node = this.nodes[i];
            const dist = Math.sqrt((x - node.x) ** 2 + (y - node.y) ** 2);
            
            if (dist < node.radius + 10) {
                // Clicked!
                this.nodes.splice(i, 1);
                this.score += Math.round(10 * (1 + node.unstability));
                break;
            }
        }
    }

    drawPlaceholder() {
        if (!this.ctx) return;
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.strokeStyle = 'rgba(34, 211, 238, 0.1)';
        this.ctx.lineWidth = 1;
        
        // Grid lines
        for(let i=0; i<this.canvas.width; i+=40) {
            this.ctx.beginPath();
            this.ctx.moveTo(i, 0);
            this.ctx.lineTo(i, this.canvas.height);
            this.ctx.stroke();
        }
        for(let i=0; i<this.canvas.height; i+=40) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, i);
            this.ctx.lineTo(this.canvas.width, i);
            this.ctx.stroke();
        }
    }

    loop() {
        if (!this.isPlaying) return;

        const now = Date.now();
        const elapsed = now - this.startTime;

        // Spawn logic
        if (now - this.lastSpawn > this.spawnRate && this.nodes.length < this.maxNodes) {
            this.spawnNode();
            this.lastSpawn = now;
            // Gradually increase difficulty
            this.spawnRate = Math.max(600, 1500 - (elapsed / 100));
        }

        // Update stability & nodes
        this.update();
        
        // Draw everything
        this.draw();

        // Update UI
        const score = document.getElementById('game-score');
        if (score) score.innerText = Math.max(0, Math.floor(this.stability));
        
        const timer = document.getElementById('game-timer');
        if (timer) timer.innerText = this.formatTime(elapsed);

        if (this.stability <= 0) {
            this.stop();
        } else {
            requestAnimationFrame(() => this.loop());
        }
    }

    update() {
        for (let i = this.nodes.length - 1; i >= 0; i--) {
            const node = this.nodes[i];
            node.unstability += node.decayRate;

            if (node.unstability >= 1) {
                this.stability -= 10;
                this.nodes.splice(i, 1);
            }
        }
        
        // Natural regeneration if stable
        if (this.nodes.length === 0) {
            this.stability = Math.min(100, this.stability + 0.05);
        }
    }

    draw() {
        if (!this.ctx) return;
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Grid
        this.drawPlaceholder();

        // Nodes
        this.nodes.forEach(node => {
            const color = this.lerpColor(this.colors.cyan, this.colors.red, node.unstability);
            
            // Outer glow
            const gradient = this.ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, node.radius * 2);
            gradient.addColorStop(0, color + '44');
            gradient.addColorStop(1, 'transparent');
            
            this.ctx.fillStyle = gradient;
            this.ctx.beginPath();
            this.ctx.arc(node.x, node.y, node.radius * 2, 0, Math.PI * 2);
            this.ctx.fill();

            // Core
            this.ctx.fillStyle = color;
            this.ctx.beginPath();
            this.ctx.arc(node.x, node.y, node.radius * (0.5 + node.unstability * 0.5), 0, Math.PI * 2);
            this.ctx.fill();

            // Ring
            this.ctx.strokeStyle = color;
            this.ctx.lineWidth = 2;
            this.ctx.beginPath();
            this.ctx.arc(node.x, node.y, node.radius + 5, 0, Math.PI * 2);
            this.ctx.stroke();
        });
    }

    lerpColor(a, b, amount) {
        const ah = parseInt(a.replace(/#/g, ''), 16),
            ar = ah >> 16, ag = ah >> 8 & 0xff, ab = ah & 0xff,
            bh = parseInt(b.replace(/#/g, ''), 16),
            br = bh >> 16, bg = bh >> 8 & 0xff, bb = bh & 0xff,
            rr = ar + amount * (br - ar),
            rg = ag + amount * (bg - ag),
            rb = ab + amount * (bb - ab);

        return '#' + ((1 << 24) + (Math.round(rr) << 16) + (Math.round(rg) << 8) + Math.round(rb)).toString(16).slice(1);
    }

    formatTime(ms) {
        const totalSecs = Math.floor(ms / 1000);
        const hours = Math.floor(totalSecs / 3600);
        const mins = Math.floor((totalSecs % 3600) / 60);
        const secs = totalSecs % 60;
        return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
}

// Initialize when DOM is ready
window.addEventListener('DOMContentLoaded', () => {
    new RayaGame();
});
