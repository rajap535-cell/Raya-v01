export class RCTClock extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: "open" });
        this.shadowRoot.innerHTML = `
            <style>
                #clock {
                    font-family: monospace;
                    color: cyan;
                    background: black;
                    padding: 10px;
                    border-radius: 8px;
                }
            </style>
            <div id="clock">Loading RCT...</div>
        `;
    }

    connectedCallback() {
        this.updateClock();
        setInterval(() => this.updateClock(), 1000);
    }

    async updateClock() {
        const res = await fetch("http://localhost:8000/rct/now");
        const data = await res.json();
        this.shadowRoot.querySelector("#clock").textContent =
            `${data.rct_ns} ns`;
    }
}

customElements.define("rct-clock", RCTClock);
