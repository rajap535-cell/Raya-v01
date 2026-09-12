

/* ==========================================================
   RAYA — VISIBLE ANIMATED STARFIELD
========================================================== */

const starCanvas =
    document.getElementById("problemStars");

const starCtx =
    starCanvas.getContext("2d");

let stars = [];


/* ==========================================================
   RESIZE
========================================================== */

function resizeStars() {

    const dpr =
        Math.min(
            window.devicePixelRatio || 1,
            2
        );

    starCanvas.width =
        window.innerWidth * dpr;

    starCanvas.height =
        window.innerHeight * dpr;

    starCanvas.style.width =
        window.innerWidth + "px";

    starCanvas.style.height =
        window.innerHeight + "px";

    starCtx.setTransform(
        dpr,
        0,
        0,
        dpr,
        0,
        0
    );

    createStars();
}


/* ==========================================================
   CREATE STARS
========================================================== */

function createStars() {

    stars = [];

    const count = 650;

    for (let i = 0; i < count; i++) {

        stars.push({

            x:
                Math.random() *
                window.innerWidth,

            y:
                Math.random() *
                window.innerHeight,

            size:
                Math.random() * 1.5 + 0.3,

            baseOpacity:
                Math.random() * 0.55 + 0.25,

            /* MUCH faster visible twinkle */
            twinkleSpeed:
                Math.random() * 0.003 +
                0.001,

            /* each star starts at different point */
            phase:
                Math.random() *
                Math.PI * 2,

            /* very slow movement */
            drift:
                Math.random() * 0.025 +
                0.005

        });

    }

}


/* ==========================================================
   ANIMATION
========================================================== */

function animateStars(time) {

    starCtx.clearRect(
        0,
        0,
        window.innerWidth,
        window.innerHeight
    );


    stars.forEach(star => {


        /* ------------------------------------------
           SLOW STAR MOVEMENT
        ------------------------------------------ */

        star.y -= star.drift;


        if (star.y < -5) {

            star.y =
                window.innerHeight + 5;

        }


        /* ------------------------------------------
           STRONGER TWINKLE
        ------------------------------------------ */

        const wave =
            Math.sin(
                time *
                star.twinkleSpeed +
                star.phase
            );


        const opacity =
            star.baseOpacity +
            wave * 0.30;


        /* ------------------------------------------
           DRAW STAR
        ------------------------------------------ */

        starCtx.beginPath();

        starCtx.arc(
            star.x,
            star.y,
            star.size,
            0,
            Math.PI * 2
        );


        starCtx.fillStyle =
            `rgba(
                220,
                240,
                255,
                ${Math.max(.05, opacity)}
            )`;


        starCtx.fill();


        /* ------------------------------------------
           BRIGHT STARS GET A SMALL GLOW
        ------------------------------------------ */

        if (star.size > 1.15) {

            starCtx.shadowBlur = 6;

            starCtx.shadowColor =
                "rgba(120,210,255,.65)";

        } else {

            starCtx.shadowBlur = 0;

        }

    });


    requestAnimationFrame(
        animateStars
    );

}


/* ==========================================================
   START
========================================================== */

resizeStars();

window.addEventListener(
    "resize",
    resizeStars
);

requestAnimationFrame(
    animateStars
);





/* ==========================================================
   RAYA — INTEGRATED EARTH
   REAL SPHERICAL PLANET + PLANETARY NETWORK
========================================================== */

const earthCanvas =
    document.getElementById(
        "earthNetworkCanvas"
    );

if (earthCanvas) {

    const ctx =
        earthCanvas.getContext("2d");


    let width;
    let height;
    let dpr;

    let cx;
    let cy;

    let earthRadius;

    let rotation = 0;

    let cloudRotation = 0;

    let networkRotation = 0;


    /* ======================================================
       EARTH SURFACE
    ====================================================== */

    const continents = [];

    for (let i = 0; i < 420; i++) {

        continents.push({

            lat:
                (Math.random() - .5)
                * Math.PI,

            lon:
                Math.random()
                * Math.PI * 2,

            size:
                Math.random() * 2.4 + .5,

            brightness:
                Math.random()

        });

    }


    /* ======================================================
       CLOUDS
    ====================================================== */

    const clouds = [];

    for (let i = 0; i < 130; i++) {

        clouds.push({

            lat:
                (Math.random() - .5)
                * Math.PI,

            lon:
                Math.random()
                * Math.PI * 2,

            size:
                Math.random() * 6 + 2

        });

    }


    /* ======================================================
       PLANETARY SYSTEMS
    ====================================================== */

    const systems = [

        {
            name: "Climate",
            lat: .65,
            lon: .20
        },

        {
            name: "Water",
            lat: .28,
            lon: 1.10
        },

        {
            name: "Energy",
            lat: -.12,
            lon: 1.90
        },

        {
            name: "Agriculture",
            lat: -.48,
            lon: 3.05
        },

        {
            name: "Health",
            lat: .20,
            lon: 4.10
        },

        {
            name: "Economy",
            lat: .55,
            lon: 5.15
        }

    ];


    /* ======================================================
       RESIZE
    ====================================================== */

    function resizeEarth() {

        dpr =
            Math.min(
                window.devicePixelRatio || 1,
                2
            );


        width =
            earthCanvas.parentElement
                .clientWidth;

        height =
            earthCanvas.parentElement
                .clientHeight;


        earthCanvas.width =
            width * dpr;

        earthCanvas.height =
            height * dpr;


        earthCanvas.style.width =
            width + "px";

        earthCanvas.style.height =
            height + "px";


        ctx.setTransform(
            dpr,
            0,
            0,
            dpr,
            0,
            0
        );


        cx =
            width / 2;

        cy =
            height / 2 - 25;


        earthRadius =
    window.innerWidth <= 800

        ? Math.min(
            115,
            height * .20,
            width * .28
        )

        : Math.min(
            185,
            height * .29,
            width * .18
        );

    }


    window.addEventListener(
        "resize",
        resizeEarth
    );


    /* ======================================================
       3D SPHERE PROJECTION
    ====================================================== */

    function project(
        lat,
        lon,
        radius,
        rot = 0
    ) {

        const longitude =
            lon + rot;


        const x =
            Math.cos(lat) *
            Math.sin(longitude);


        const y =
            Math.sin(lat);


        const z =
            Math.cos(lat) *
            Math.cos(longitude);


        return {

            x:
                cx + x * radius,

            y:
                cy - y * radius,

            z:
                z

        };

    }


    /* ======================================================
       EARTH
    ====================================================== */

    function drawEarth() {

        ctx.save();


        ctx.beginPath();

        ctx.arc(
            cx,
            cy,
            earthRadius,
            0,
            Math.PI * 2
        );

        ctx.clip();


        /* ----------------------------------------------
           OCEAN
        ---------------------------------------------- */

        const ocean =
            ctx.createRadialGradient(

                cx - 70,
                cy - 75,
                15,

                cx,
                cy,
                earthRadius

            );


        ocean.addColorStop(
            0,
            "#1475ad"
        );

        ocean.addColorStop(
            .35,
            "#07517f"
        );

        ocean.addColorStop(
            .70,
            "#033355"
        );

        ocean.addColorStop(
            1,
            "#010b18"
        );


        ctx.fillStyle =
            ocean;


        ctx.fillRect(

            cx - earthRadius,
            cy - earthRadius,

            earthRadius * 2,
            earthRadius * 2

        );


        /* ----------------------------------------------
           NIGHT SIDE
        ---------------------------------------------- */

        const shadow =
            ctx.createLinearGradient(

                cx - earthRadius,
                cy,

                cx + earthRadius,
                cy

            );


        shadow.addColorStop(
            0,
            "rgba(0,0,0,.05)"
        );

        shadow.addColorStop(
            .55,
            "rgba(0,0,0,.18)"
        );

        shadow.addColorStop(
            1,
            "rgba(0,0,0,.88)"
        );


        ctx.fillStyle =
            shadow;


        ctx.fillRect(

            cx - earthRadius,
            cy - earthRadius,

            earthRadius * 2,
            earthRadius * 2

        );


        /* ----------------------------------------------
           LAND
        ---------------------------------------------- */

        continents.forEach(
            point => {

                const pos =
                    project(
                        point.lat,
                        point.lon,
                        earthRadius - 3,
                        rotation
                    );


                if (
                    pos.z <= 0
                )
                    return;


                const opacity =
                    .16 +
                    pos.z * .55;


                ctx.beginPath();


                ctx.arc(

                    pos.x,
                    pos.y,

                    point.size *
                    (.65 + pos.z * .5),

                    0,
                    Math.PI * 2

                );


                if (
                    point.brightness > .72
                ) {

                    ctx.fillStyle =
                        `rgba(
                            105,
                            210,
                            145,
                            ${opacity}
                        )`;

                } else {

                    ctx.fillStyle =
                        `rgba(
                            35,
                            125,
                            90,
                            ${opacity}
                        )`;

                }


                ctx.fill();

            }
        );


        /* ----------------------------------------------
           CLOUDS
        ---------------------------------------------- */

        clouds.forEach(
            cloud => {

                const pos =
                    project(
                        cloud.lat,
                        cloud.lon,
                        earthRadius,
                        cloudRotation
                    );


                if (
                    pos.z <= 0
                )
                    return;


                ctx.beginPath();


                ctx.arc(

                    pos.x,
                    pos.y,

                    cloud.size *
                    pos.z,

                    0,
                    Math.PI * 2

                );


                ctx.fillStyle =
                    `rgba(
                        255,
                        255,
                        255,
                        ${.025 + pos.z * .10}
                    )`;


                ctx.fill();

            }
        );


        ctx.restore();


        /* ----------------------------------------------
           ATMOSPHERIC RIM
        ---------------------------------------------- */

        ctx.beginPath();

        ctx.arc(
            cx,
            cy,
            earthRadius,
            0,
            Math.PI * 2
        );


        ctx.strokeStyle =
            "rgba(70,220,255,.65)";


        ctx.lineWidth =
            1.5;


        ctx.shadowColor =
            "rgba(30,200,255,.7)";


        ctx.shadowBlur =
            18;


        ctx.stroke();


        ctx.shadowBlur = 0;

    }


    /* ======================================================
       PLANETARY NETWORK
    ====================================================== */

    /* ======================================================
   PLANETARY NETWORK — SYMMETRICAL SIX SYSTEMS
====================================================== */

function drawNetwork() {

    /*
     * Six systems arranged at exactly 60° intervals.
     *
     *              Climate
     *
     *       Health       Energy
     *
     *       Agriculture  Economy
     *
     *              Water
     *
     * All boxes are outside the Earth.
     */

    const isMobile = window.innerWidth <= 800;

const boxWidth = isMobile ? 88 : 128;
const boxHeight = isMobile ? 34 : 42;

    /*
     * Distance between Earth and the BOX CENTER.
     * Increase this if you want the boxes farther away.
     */
    const orbitRadius =
        earthRadius + 110;


    /* ==================================================
       FIXED SYMMETRICAL ORDER
    ================================================== */

    const layout = window.innerWidth <= 800 ? [

        {
            name: "Climate",
            angle: -Math.PI / 2
        },

        {
            name: "Energy",
            angle: -Math.PI / 6
        },

        {
            name: "Economy",
            angle: Math.PI / 6
        },

        {
            name: "Water",
            angle: Math.PI / 2
        },

        {
            name: "Agriculture",
            angle: 5 * Math.PI / 6
        },

        {
            name: "Health",
            angle: 7 * Math.PI / 6
        }
    ]
    : [

        {
            name: "Climate",
            angle: -Math.PI / 2
        },

        {
            name: "Energy",
            angle: -Math.PI / 6
        },

        {
            name: "Economy",
            angle: Math.PI / 6
        },

        {
            name: "Water",
            angle: Math.PI / 2
        },

        {
            name: "Agriculture",
            angle: 5 * Math.PI / 6
        },

        {
            name: "Health",
            angle: 7 * Math.PI / 6
        }

    ];


    /* ==================================================
       CREATE POSITIONS
    ================================================== */

    const projected =
    layout.map((item, index) => {

        const dx =
            Math.cos(item.angle);

        const dy =
            Math.sin(item.angle);


        /*
         * TOP + BOTTOM
         * stay closer to Earth.
         *
         * SIDE SYSTEMS
         * stay farther away.
         */

        let orbitRadius;


        if (isMobile) {

    orbitRadius =
        earthRadius + 42;

} else if (
    item.name === "Climate" ||
    item.name === "Water"
) {

    orbitRadius =
        earthRadius + 65;

} else {

    orbitRadius =
        earthRadius + 135;

}


        return {

            name:
                item.name,

            angle:
                item.angle,

            index,

            x:
                cx +
                dx * orbitRadius,

            y:
                cy +
                dy * orbitRadius

        };

    });




    /* ==================================================
       DRAW CONNECTIONS
    ================================================== */

    projected.forEach(item => {

        const dx =
            Math.cos(item.angle);

        const dy =
            Math.sin(item.angle);


        /*
         * Start exactly at Earth's outer edge.
         */
        const earthX =
            cx +
            dx *
            (earthRadius + 2);

        const earthY =
            cy +
            dy *
            (earthRadius + 2);


        /*
         * Find where the line should stop:
         * at the EDGE of the rectangular box,
         * not at its center.
         */

        const halfW =
            boxWidth / 2;

        const halfH =
            boxHeight / 2;


        const distanceToBox =
            Math.min(

                Math.abs(dx) > 0.001
                    ? halfW / Math.abs(dx)
                    : Infinity,

                Math.abs(dy) > 0.001
                    ? halfH / Math.abs(dy)
                    : Infinity

            );


        const boxX =
            item.x -
            dx * (distanceToBox + 4);

        const boxY =
            item.y -
            dy * (distanceToBox + 4);


        /* ------------------------------------------
           MAIN CONNECTOR
        ------------------------------------------ */

        ctx.beginPath();

        ctx.moveTo(
            earthX,
            earthY
        );

        ctx.lineTo(
            boxX,
            boxY
        );

        ctx.strokeStyle =
            "rgba(34,232,255,.34)";

        ctx.lineWidth = 1;

        ctx.shadowColor =
            "rgba(34,232,255,.45)";

        ctx.shadowBlur = 6;

        ctx.stroke();

        ctx.shadowBlur = 0;


        /* ------------------------------------------
           ANIMATED DATA PULSE
        ------------------------------------------ */

        const pulse =
            (
                Date.now() * 0.00022 +
                item.index * 0.16
            ) % 1;


        const pulseX =
            earthX +
            (boxX - earthX) *
            pulse;


        const pulseY =
            earthY +
            (boxY - earthY) *
            pulse;


        ctx.beginPath();

        ctx.arc(
            pulseX,
            pulseY,
            2.2,
            0,
            Math.PI * 2
        );

        ctx.fillStyle =
            "#6ff5ff";

        ctx.shadowColor =
            "#22e8ff";

        ctx.shadowBlur = 12;

        ctx.fill();

        ctx.shadowBlur = 0;

    });


    /* ==================================================
       DRAW SYSTEM BOXES
    ================================================== */

    projected.forEach(item => {

        const x =
            item.x -
            boxWidth / 2;

        const y =
            item.y -
            boxHeight / 2;


        /* ------------------------------------------
           BOX
        ------------------------------------------ */

        ctx.beginPath();

        ctx.roundRect(
            x,
            y,
            boxWidth,
            boxHeight,
            5
        );


        ctx.fillStyle =
            "rgba(5,24,42,.88)";

        ctx.fill();


        ctx.strokeStyle =
            "rgba(34,232,255,.45)";

        ctx.lineWidth = 1;

        ctx.shadowColor =
            "rgba(34,232,255,.35)";

        ctx.shadowBlur = 12;

        ctx.stroke();

        ctx.shadowBlur = 0;


        /* ------------------------------------------
           TECH CORNERS
        ------------------------------------------ */

        const corner = 8;


        ctx.strokeStyle =
            "#54eaff";

        ctx.lineWidth = 1.5;


        /* TOP LEFT */

        ctx.beginPath();

        ctx.moveTo(
            x,
            y + corner
        );

        ctx.lineTo(
            x,
            y
        );

        ctx.lineTo(
            x + corner,
            y
        );

        ctx.stroke();


        /* TOP RIGHT */

        ctx.beginPath();

        ctx.moveTo(
            x + boxWidth - corner,
            y
        );

        ctx.lineTo(
            x + boxWidth,
            y
        );

        ctx.lineTo(
            x + boxWidth,
            y + corner
        );

        ctx.stroke();


        /* BOTTOM LEFT */

        ctx.beginPath();

        ctx.moveTo(
            x,
            y + boxHeight - corner
        );

        ctx.lineTo(
            x,
            y + boxHeight
        );

        ctx.lineTo(
            x + corner,
            y + boxHeight
        );

        ctx.stroke();


        /* BOTTOM RIGHT */

        ctx.beginPath();

        ctx.moveTo(
            x + boxWidth - corner,
            y + boxHeight
        );

        ctx.lineTo(
            x + boxWidth,
            y + boxHeight
        );

        ctx.lineTo(
            x + boxWidth,
            y + boxHeight - corner
        );

        ctx.stroke();


        /* ------------------------------------------
           SYSTEM NAME
        ------------------------------------------ */

        ctx.font =
            "500 12px Inter, sans-serif";

        ctx.textAlign =
            "center";

        ctx.textBaseline =
            "middle";

        ctx.fillStyle =
            "#dceff7";

        ctx.fillText(
            item.name,
            item.x,
            item.y
        );


        /* ------------------------------------------
           SMALL SIGNAL NODE
        ------------------------------------------ */

        ctx.beginPath();

        ctx.arc(
            item.x,
            item.y +
            boxHeight / 2 +
            10,
            2.5,
            0,
            Math.PI * 2
        );

        ctx.fillStyle =
            "#6ff5ff";

        ctx.shadowColor =
            "#22e8ff";

        ctx.shadowBlur = 12;

        ctx.fill();

        ctx.shadowBlur = 0;

    });

}


    /* ======================================================
       ATMOSPHERIC GLOW
    ====================================================== */

    function drawGlow() {

        const glow =
            ctx.createRadialGradient(

                cx,
                cy,
                earthRadius * .55,

                cx,
                cy,
                earthRadius * 1.65

            );


        glow.addColorStop(
            0,
            "rgba(20,150,255,.08)"
        );

        glow.addColorStop(
            .55,
            "rgba(20,110,220,.05)"
        );

        glow.addColorStop(
            1,
            "rgba(0,50,120,0)"
        );


        ctx.beginPath();


        ctx.arc(

            cx,
            cy,

            earthRadius * 1.65,

            0,
            Math.PI * 2

        );


        ctx.fillStyle =
            glow;


        ctx.fill();

    }


    /* ======================================================
       ANIMATION
    ====================================================== */

    function animateEarth() {

        ctx.clearRect(
            0,
            0,
            width,
            height
        );


        drawGlow();

        drawEarth();

        drawNetwork();


        /* Very slow Earth rotation */

        rotation +=
            .00045;


        /* Clouds slightly faster */

        cloudRotation +=
            .00065;


        /* Network almost stationary */

        networkRotation +=
            .00005;


        requestAnimationFrame(
            animateEarth
        );

    }


    resizeEarth();

    animateEarth();

}



/* ==========================================================
   RAYA — HUMAN FRAGMENTATION
   ISOLATED SYSTEMS / FAILED CONNECTIONS
========================================================== */

const fragmentationCanvas =
    document.getElementById("fragmentationCanvas");

if (fragmentationCanvas) {

    const fctx =
        fragmentationCanvas.getContext("2d");


    let fw;
    let fh;
    let fdpr;


    /* ======================================================
       SYSTEM NODES
    ====================================================== */

    const fragmentationNodes = window.innerWidth <= 800

    ? [

        {
            name: "Climate",
            x: .50,
            y: .27
        },

        {
            name: "Energy",
            x: .34,
            y: .43
        },

        {
            name: "Water",
            x: .66,
            y: .43
        },

        {
            name: "Agriculture",
            x: .34,
            y: .64
        },

        {
            name: "Markets",
            x: .66,
            y: .64
        },

        {
            name: "Health",
            x: .50,
            y: .80
        }

    ]

    : [

        {
            name: "Climate",
            x: .50,
            y: .30
        },

        {
            name: "Energy",
            x: .28,
            y: .48
        },

        {
            name: "Water",
            x: .72,
            y: .48
        },

        {
            name: "Agriculture",
            x: .35,
            y: .72
        },

        {
            name: "Markets",
            x: .65,
            y: .72
        },

        {
            name: "Health",
            x: .50,
            y: .88
        }

    ];


    /* ======================================================
       FAILED CONNECTIONS
    ====================================================== */

    const connections = [

        [0, 1],
        [0, 2],
        [1, 3],
        [2, 4],
        [3, 4],
        [1, 2],
        [3, 5],
        [4, 5],
        [0, 5]

    ];


    /* ======================================================
       ANIMATED CONNECTION ATTEMPTS
    ====================================================== */

    let connectionAttempts = [];


    function createConnectionAttempt() {

    const connection =
        connections[
            Math.floor(
                Math.random() *
                connections.length
            )
        ];


    /*
     * Each connection gets its own failure point.
     *
     * Some connections fail early.
     * Some get very close.
     */

    const failurePoint =
        .55 +
        Math.random() * .37;


    connectionAttempts.push({

        from: connection[0],

        to: connection[1],

        progress: 0,

        speed:
            .0025 +
            Math.random() * .003,

        /*
         * Where this particular connection
         * will disappear.
         */

        failurePoint:
            failurePoint,

        life: 0,

        maxLife:
            180 +
            Math.random() * 220

    });

}


    /* ======================================================
       RESIZE
    ====================================================== */

    function resizeFragmentation() {

        fdpr =
            Math.min(
                window.devicePixelRatio || 1,
                2
            );


        fw =
            fragmentationCanvas
                .parentElement
                .clientWidth;


        fh =
            fragmentationCanvas
                .parentElement
                .clientHeight;


        fragmentationCanvas.width =
            fw * fdpr;


        fragmentationCanvas.height =
            fh * fdpr;


        fragmentationCanvas.style.width =
            fw + "px";


        fragmentationCanvas.style.height =
            fh + "px";


        fctx.setTransform(
            fdpr,
            0,
            0,
            fdpr,
            0,
            0
        );

    }


    /* ======================================================
       NODE POSITION
    ====================================================== */

    function nodePosition(node) {

        return {

            x:
                node.x * fw,

            y:
                node.y * fh

        };

    }


    /* ======================================================
       DRAW BROKEN CONNECTION
    ====================================================== */

    function drawBrokenConnection(a, b) {

        const start =
            nodePosition(a);

        const end =
            nodePosition(b);


        const dx =
            end.x - start.x;

        const dy =
            end.y - start.y;


        const distance =
            Math.sqrt(
                dx * dx +
                dy * dy
            );


        const gap =
            28;


        const ux =
            dx / distance;

        const uy =
            dy / distance;


        /*
         * Leave a visible gap in the middle.
         */

        const middle =
            distance / 2;


        const firstEnd =
            middle - gap;


        const secondStart =
            middle + gap;


        /* ------------------------------------------
           FIRST BROKEN SEGMENT
        ------------------------------------------ */

        fctx.beginPath();

        fctx.moveTo(
            start.x,
            start.y
        );

        fctx.lineTo(
            start.x + ux * firstEnd,
            start.y + uy * firstEnd
        );

        fctx.strokeStyle =
            "rgba(80,180,225,.38)";

        fctx.lineWidth = 1;

        fctx.setLineDash([5, 8]);

        fctx.stroke();


        /* ------------------------------------------
           SECOND BROKEN SEGMENT
        ------------------------------------------ */

        fctx.beginPath();

        fctx.moveTo(
            start.x + ux * secondStart,
            start.y + uy * secondStart
        );

        fctx.lineTo(
            end.x,
            end.y
        );

        fctx.strokeStyle =
            "rgba(80,180,235,.38)";

        fctx.lineWidth = 1;

        fctx.setLineDash([5, 8]);

        fctx.stroke();


        fctx.setLineDash([]);


        /* ------------------------------------------
           FAILURE MARK
        ------------------------------------------ */

        const gapX =
            start.x +
            ux * middle;


        const gapY =
            start.y +
            uy * middle;


        fctx.strokeStyle =
            "rgba(34,232,255,.48)";

        fctx.lineWidth = 1;


        fctx.beginPath();

        fctx.moveTo(
            gapX - 4,
            gapY - 4
        );

        fctx.lineTo(
            gapX + 4,
            gapY + 4
        );

        fctx.moveTo(
            gapX + 4,
            gapY - 4
        );

        fctx.lineTo(
            gapX - 4,
            gapY + 4
        );

        fctx.stroke();

    }


    /* ======================================================
       DRAW CONNECTION ATTEMPT
    ====================================================== */

    function drawAttempt(attempt) {

    const from =
        nodePosition(
            fragmentationNodes[
                attempt.from
            ]
        );


    const to =
        nodePosition(
            fragmentationNodes[
                attempt.to
            ]
        );


    /* ==================================================
       CONNECTION PROGRESS
    ================================================== */

    const progress =
        Math.min(
            attempt.progress,
            attempt.failurePoint
        );


    const x =
        from.x +
        (to.x - from.x) *
        progress;


    const y =
        from.y +
        (to.y - from.y) *
        progress;


    /* ==================================================
       FAILURE APPROACH
       
       When the signal gets close to its individual
       failure point, introduce a subtle red warning.
    ================================================== */

    const warningStart =
        attempt.failurePoint - .12;


    let warning =
        0;


    if (
        progress > warningStart
    ) {

        warning =
            (
                progress -
                warningStart
            ) /
            (
                attempt.failurePoint -
                warningStart
            );

    }


    warning =
        Math.max(
            0,
            Math.min(
                1,
                warning
            )
        );


    /*
     * Smooth warning intensity.
     */

    warning =
        warning * warning;


    /* ==================================================
       CYAN SIGNAL
    ================================================== */

    fctx.beginPath();

    fctx.arc(
        x,
        y,
        2.5 + warning * 1.2,
        0,
        Math.PI * 2
    );


    /*
     * Transition from cyan → subtle red.
     */

    const cyan =
        Math.round(
            111 -
            warning * 40
        );


    const green =
        Math.round(
            245 -
            warning * 165
        );


    const blue =
        Math.round(
            255 -
            warning * 170
        );


    fctx.fillStyle =
        `rgba(
            255,
            ${green},
            ${blue},
            .95
        )`;


    fctx.shadowColor =
        warning > 0
            ? `rgba(
                255,
                70,
                65,
                ${warning * .55}
            )`
            : "#22e8ff";


    fctx.shadowBlur =
        warning > 0
            ? 10 + warning * 12
            : 12;


    fctx.fill();

    fctx.shadowBlur = 0;


    /* ==================================================
       SIGNAL TRAIL
    ================================================== */

    const trailProgress =
        Math.max(
            0,
            progress - .09
        );


    const trailX =
        from.x +
        (to.x - from.x) *
        trailProgress;


    const trailY =
        from.y +
        (to.y - from.y) *
        trailProgress;


    fctx.beginPath();

    fctx.moveTo(
        trailX,
        trailY
    );

    fctx.lineTo(
        x,
        y
    );


    fctx.strokeStyle =
        warning > 0
            ? `rgba(
                255,
                80,
                70,
                ${warning * .28}
            )`
            : "rgba(34,232,255,.42)";


    fctx.lineWidth =
        1.5;


    fctx.stroke();


    /* ==================================================
       SUBTLE FAILURE GLOW
    ================================================== */

    if (warning > 0) {

        const glowRadius =
            8 +
            warning * 12;


        const glow =
            fctx.createRadialGradient(

                x,
                y,
                0,

                x,
                y,
                glowRadius

            );


        glow.addColorStop(
            0,
            `rgba(
                255,
                70,
                60,
                ${warning * .18}
            )`
        );


        glow.addColorStop(
            1,
            "rgba(255,70,60,0)"
        );


        fctx.beginPath();

        fctx.arc(
            x,
            y,
            glowRadius,
            0,
            Math.PI * 2
        );


        fctx.fillStyle =
            glow;

        fctx.fill();

    }

}


    /* ======================================================
       DRAW NODE
    ====================================================== */

    function drawNode(node, index, time) {

        const pos =
            nodePosition(node);


        /*
         * Gentle floating movement
         */

        const floatY =
            Math.sin(
                time * .001 +
                index * 1.4
            ) * 4;


        const x =
            pos.x;


        const y =
            pos.y +
            floatY;


        const pulse =
            1 +
            Math.sin(
                time * .002 +
                index
            ) * .12;


       const isMobile = window.innerWidth <= 800;

const boxWidth = isMobile ? 92 : 120;
const boxHeight = isMobile ? 36 : 42;


        /* ------------------------------------------
           NODE GLOW
        ------------------------------------------ */

        fctx.beginPath();

        fctx.arc(
            x,
            y,
            18 * pulse,
            0,
            Math.PI * 2
        );


        fctx.fillStyle =
            "rgba(34,232,255,.035)";

        fctx.shadowColor =
            "rgba(34,232,255,.45)";

        fctx.shadowBlur =
            20;

        fctx.fill();

        fctx.shadowBlur = 0;


        /* ------------------------------------------
           BOX
        ------------------------------------------ */

        fctx.beginPath();

        fctx.roundRect(
            x - boxWidth / 2,
            y - boxHeight / 2,
            boxWidth,
            boxHeight,
            6
        );


        fctx.fillStyle =
            "rgba(5,20,36,.88)";

        fctx.fill();


        fctx.strokeStyle =
            "rgba(60,190,225,.38)";

        fctx.lineWidth = 1;

        fctx.stroke();


        /* ------------------------------------------
           NODE DOT
        ------------------------------------------ */

        fctx.beginPath();

        fctx.arc(
            x,
            y - boxHeight / 2 - 8,
            2.5,
            0,
            Math.PI * 2
        );


        fctx.fillStyle =
            "#6ff5ff";

        fctx.shadowColor =
            "#22e8ff";

        fctx.shadowBlur =
            10;

        fctx.fill();

        fctx.shadowBlur = 0;


        /* ------------------------------------------
           LABEL
        ------------------------------------------ */

        fctx.font =
            "500 12px Inter, sans-serif";

        fctx.textAlign =
            "center";

        fctx.textBaseline =
            "middle";

        fctx.fillStyle =
            "#dceff7";


        fctx.fillText(
            node.name,
            x,
            y
        );

    }


    /* ======================================================
       ANIMATION
    ====================================================== */

    function animateFragmentation(time) {

        fctx.clearRect(
            0,
            0,
            fw,
            fh
        );


        /* ------------------------------------------
           BROKEN CONNECTIONS
        ------------------------------------------ */

        connections.forEach(
            connection => {

                drawBrokenConnection(

                    fragmentationNodes[
                        connection[0]
                    ],

                    fragmentationNodes[
                        connection[1]
                    ]

                );

            }
        );


        /* ------------------------------------------
           CONNECTION ATTEMPTS
        ------------------------------------------ */

        connectionAttempts.forEach(
            attempt => {

                attempt.progress +=
                    attempt.speed;

                attempt.life++;

                drawAttempt(
                    attempt
                );

            }
        );


        /*
         * Remove failed attempts.
         */

        connectionAttempts =
    connectionAttempts.filter(
        attempt =>
            attempt.progress <
            attempt.failurePoint &&
            attempt.life <
            attempt.maxLife
    );


        /*
         * Occasionally create a new attempt.
         */

       if (
    Math.random() < .008 &&
    connectionAttempts.length < 3
) {

    createConnectionAttempt();

}


        /* ------------------------------------------
           NODES
        ------------------------------------------ */

        fragmentationNodes.forEach(
            (node, index) => {

                drawNode(
                    node,
                    index,
                    time
                );

            }
        );


        requestAnimationFrame(
            animateFragmentation
        );

    }


    /* ======================================================
       START
    ====================================================== */

    resizeFragmentation();

    window.addEventListener(
        "resize",
        resizeFragmentation
    );


    requestAnimationFrame(
        animateFragmentation
    );

}



/* ==========================================================
   RAYA — ENERGY NETWORK
   POWER / SOLAR / WIND / TRANSMISSION / CITIES
========================================================== */

const energyCanvas =
    document.getElementById("energyNetworkCanvas");

if (energyCanvas) {

    const ectx =
        energyCanvas.getContext("2d");

    let ew;
    let eh;
    let edpr;


    /* ======================================================
       ENERGY SYSTEMS
    ====================================================== */

    const energyNodes = [

        {
            name: "SOLAR",
            type: "solar",
            x: .18,
            y: .30
        },

        {
            name: "POWER PLANTS",
            type: "plant",
            x: .18,
            y: .68
        },

        {
            name: "WIND",
            type: "wind",
            x: .82,
            y: .30
        },

        {
            name: "TRANSMISSION",
            type: "grid",
            x: .82,
            y: .68
        },

        {
            name: "CITIES",
            type: "city",
            x: .50,
            y: .10
        },

        {
            name: "STORAGE",
            type: "storage",
            x: .50,
            y: .92
        }

    ];


    /* ======================================================
       RESIZE
    ====================================================== */

    function resizeEnergy() {

        edpr =
            Math.min(
                window.devicePixelRatio || 1,
                2
            );

        ew =
            energyCanvas.parentElement.clientWidth;

        eh =
            energyCanvas.parentElement.clientHeight;

        energyCanvas.width =
            ew * edpr;

        energyCanvas.height =
            eh * edpr;

        energyCanvas.style.width =
            ew + "px";

        energyCanvas.style.height =
            eh + "px";

        ectx.setTransform(
            edpr,
            0,
            0,
            edpr,
            0,
            0
        );

    }


    /* ======================================================
       NODE POSITION
    ====================================================== */

    function nodePosition(node) {

        return {

            x: node.x * ew,

            y: node.y * eh

        };

    }


    /* ======================================================
       DRAW ENERGY NODE
    ====================================================== */

    function drawEnergyNode(
        node,
        index,
        time
    ) {

        const pos =
            nodePosition(node);


        const pulse =
            1 +
            Math.sin(
                time * .002 +
                index * 1.4
            ) * .10;


        const radius =
    Math.min(26, ew * .065) * pulse;


        /* ------------------------------------------
           GLOW
        ------------------------------------------ */

        const glow =
            ectx.createRadialGradient(

                pos.x,
                pos.y,
                0,

                pos.x,
                pos.y,
                radius * 2.4

            );


        glow.addColorStop(
            0,
            "rgba(34,232,255,.16)"
        );

        glow.addColorStop(
            .45,
            "rgba(34,180,255,.06)"
        );

        glow.addColorStop(
            1,
            "rgba(34,180,255,0)"
        );


        ectx.beginPath();

        ectx.arc(
            pos.x,
            pos.y,
            radius * 2.4,
            0,
            Math.PI * 2
        );

        ectx.fillStyle =
            glow;

        ectx.fill();


        /* ------------------------------------------
           NODE CORE
        ------------------------------------------ */

        ectx.beginPath();

        ectx.arc(
            pos.x,
            pos.y,
            radius,
            0,
            Math.PI * 2
        );

        ectx.fillStyle =
            "rgba(4,20,36,.92)";

        ectx.fill();


        ectx.strokeStyle =
            "rgba(34,232,255,.48)";

        ectx.lineWidth = 1;

        ectx.shadowColor =
            "rgba(34,232,255,.65)";

        ectx.shadowBlur = 12;

        ectx.stroke();

        ectx.shadowBlur = 0;


        /* ------------------------------------------
           NODE SYMBOL
        ------------------------------------------ */

        drawEnergySymbol(
            node.type,
            pos.x,
            pos.y
        );


        /* ------------------------------------------
           LABEL
        ------------------------------------------ */

        ectx.font =
    `500 ${Math.max(8, Math.min(11, ew * .028))}px Inter, sans-serif`;

        ectx.textAlign =
            "center";

        ectx.textBaseline =
            "top";

        ectx.fillStyle =
            "#cfe5ef";

        ectx.fillText(
            node.name,
            pos.x,
            pos.y + radius + 10
        );

    }


    /* ======================================================
       SIMPLE TECHNICAL SYMBOLS
    ====================================================== */

    function drawEnergySymbol(
        type,
        x,
        y
    ) {

        ectx.save();

        ectx.translate(
            x,
            y
        );

        ectx.strokeStyle =
            "#55eaff";

        ectx.fillStyle =
            "#55eaff";

        ectx.lineWidth = 2;

        ectx.shadowColor =
            "#22e8ff";

        ectx.shadowBlur = 8;


        /* SOLAR */

        if (type === "solar") {

            ectx.strokeRect(
                -12,
                -8,
                24,
                16
            );

            ectx.beginPath();

            ectx.moveTo(
                -6,
                -8
            );

            ectx.lineTo(
                -6,
                8
            );

            ectx.moveTo(
                0,
                -8
            );

            ectx.lineTo(
                0,
                8
            );

            ectx.moveTo(
                6,
                -8
            );

            ectx.lineTo(
                6,
                8
            );

            ectx.stroke();

        }


        /* POWER PLANT */

        else if (type === "plant") {

            ectx.fillRect(
                -12,
                -7,
                24,
                14
            );

            ectx.clearRect(
                -8,
                -4,
                5,
                8
            );

            ectx.clearRect(
                3,
                -4,
                5,
                8
            );

        }


        /* WIND */

        else if (type === "wind") {

            ectx.beginPath();

            ectx.arc(
                0,
                0,
                3,
                0,
                Math.PI * 2
            );

            ectx.stroke();

            for (
                let i = 0;
                i < 3;
                i++
            ) {

                const angle =
                    i *
                    Math.PI *
                    2 / 3;

                ectx.beginPath();

                ectx.moveTo(
                    0,
                    0
                );

                ectx.lineTo(
                    Math.cos(angle) * 13,
                    Math.sin(angle) * 13
                );

                ectx.stroke();

            }

        }


        /* TRANSMISSION */

        else if (type === "grid") {

            ectx.beginPath();

            ectx.moveTo(
                -12,
                10
            );

            ectx.lineTo(
                0,
                -10
            );

            ectx.lineTo(
                12,
                10
            );

            ectx.stroke();

            ectx.beginPath();

            ectx.moveTo(
                -7,
                2
            );

            ectx.lineTo(
                7,
                2
            );

            ectx.stroke();

        }


        /* CITY */

        else if (type === "city") {

            ectx.strokeRect(
                -10,
                -13,
                8,
                26
            );

            ectx.strokeRect(
                2,
                -7,
                9,
                20
            );

        }


        /* STORAGE */

        else {

            ectx.strokeRect(
                -10,
                -12,
                20,
                24
            );

            ectx.beginPath();

            ectx.moveTo(
                -5,
                -6
            );

            ectx.lineTo(
                5,
                -6
            );

            ectx.moveTo(
                -5,
                0
            );

            ectx.lineTo(
                5,
                0
            );

            ectx.moveTo(
                -5,
                6
            );

            ectx.lineTo(
                5,
                6
            );

            ectx.stroke();

        }


        ectx.restore();

    }


    /* ======================================================
       LOCAL ENERGY SIGNALS
       
       These are NOT global connections.
       They represent systems operating independently.
    ====================================================== */

    function drawLocalSignals(time) {

        energyNodes.forEach(
            (node, index) => {

                const pos =
                    nodePosition(node);


                const phase =
                    (
                        time * .00035 +
                        index * .21
                    ) % 1;


                const angle =
                    index *
                    1.7;


                const distance =
                    30 +
                    phase * 55;


                const x =
                    pos.x +
                    Math.cos(angle) *
                    distance;


                const y =
                    pos.y +
                    Math.sin(angle) *
                    distance;


                ectx.beginPath();

                ectx.arc(
                    x,
                    y,
                    1.8,
                    0,
                    Math.PI * 2
                );


                ectx.fillStyle =
                    "rgba(90,235,255,.72)";

                ectx.shadowColor =
                    "#22e8ff";

                ectx.shadowBlur = 9;

                ectx.fill();

                ectx.shadowBlur = 0;

            }
        );

    }


    /* ======================================================
       VERY SUBTLE NON-CONNECTIONS
       
       Short local lines show activity,
       but they never connect the systems.
    ====================================================== */

    function drawLocalActivity() {

        energyNodes.forEach(
            (node, index) => {

                const pos =
                    nodePosition(node);


                const angle =
                    index * 1.7;


                const length = 48;


                ectx.beginPath();

                ectx.moveTo(
                    pos.x +
                    Math.cos(angle) * 30,

                    pos.y +
                    Math.sin(angle) * 30
                );


                ectx.lineTo(
                    pos.x +
                    Math.cos(angle) * length,

                    pos.y +
                    Math.sin(angle) * length
                );


                ectx.strokeStyle =
                    "rgba(34,232,255,.12)";

                ectx.lineWidth = 1;

                ectx.stroke();

            }
        );

    }


    /* ======================================================
       ANIMATION
    ====================================================== */

    function animateEnergy(time) {

        ectx.clearRect(
            0,
            0,
            ew,
            eh
        );


        drawLocalActivity();

        drawLocalSignals(time);


        energyNodes.forEach(
            (node, index) => {

                drawEnergyNode(
                    node,
                    index,
                    time
                );

            }
        );


        requestAnimationFrame(
            animateEnergy
        );

    }


    /* ======================================================
       START
    ====================================================== */

    resizeEnergy();

    window.addEventListener(
        "resize",
        resizeEnergy
    );

    requestAnimationFrame(
        animateEnergy
    );

}



/* ==========================================================
   RAYA — FOOD SYSTEM NETWORK
   FARMLAND / WEATHER / SATELLITES / FARMERS / MARKETS
========================================================== */

const foodCanvas =
    document.getElementById("foodNetworkCanvas");

if (foodCanvas) {

    const fctx =
        foodCanvas.getContext("2d");

    let fw;
    let fh;
    let fdpr;


    /* ======================================================
       FOOD SYSTEM NODES
    ====================================================== */

    const foodNodes = window.innerWidth <= 800

    ? [

        {
            name: "WEATHER",
            x: .27,
            y: .28,
            icon: "weather"
        },

        {
            name: "SATELLITES",
            x: .73,
            y: .28,
            icon: "satellite"
        },

        {
            name: "FARMERS",
            x: .27,
            y: .72,
            icon: "farmer"
        },

        {
            name: "MARKETS",
            x: .73,
            y: .72,
            icon: "market"
        }

    ]

    : [

        {
            name: "WEATHER",
            x: .17,
            y: .28,
            icon: "weather"
        },

        {
            name: "SATELLITES",
            x: .82,
            y: .27,
            icon: "satellite"
        },

        {
            name: "FARMERS",
            x: .18,
            y: .72,
            icon: "farmer"
        },

        {
            name: "MARKETS",
            x: .82,
            y: .72,
            icon: "market"
        }

    ];


    /* ======================================================
       RESIZE
    ====================================================== */

    function resizeFood() {

        fdpr =
            Math.min(
                window.devicePixelRatio || 1,
                2
            );

        fw =
            foodCanvas.parentElement.clientWidth;

        fh =
            foodCanvas.parentElement.clientHeight;

        foodCanvas.width =
            fw * fdpr;

        foodCanvas.height =
            fh * fdpr;

        foodCanvas.style.width =
            fw + "px";

        foodCanvas.style.height =
            fh + "px";

        fctx.setTransform(
            fdpr,
            0,
            0,
            fdpr,
            0,
            0
        );

    }


    /* ======================================================
       NODE POSITION
    ====================================================== */

    function foodNodePosition(node) {

        return {

            x: node.x * fw,

            y: node.y * fh

        };

    }


    /* ======================================================
       DRAW CONNECTION
       
       IMPORTANT:
       Connections are intentionally faint.
       The systems are visible, but not strongly coordinated.
    ====================================================== */

    function drawFoodConnection(
        a,
        b,
        index,
        time
    ) {

        const start =
            foodNodePosition(a);

        const end =
            foodNodePosition(b);


        fctx.beginPath();

        fctx.moveTo(
            start.x,
            start.y
        );

        fctx.lineTo(
            end.x,
            end.y
        );


        fctx.strokeStyle =
            "rgba(90,210,235,.20)";

        fctx.lineWidth = 1;

        fctx.setLineDash([3, 10]);

        fctx.stroke();

        fctx.setLineDash([]);


        /* ------------------------------------------
           MOVING DATA SIGNAL
        ------------------------------------------ */

        const progress =
            (
                time * .00012 +
                index * .25
            ) % 1;


        const x =
            start.x +
            (end.x - start.x) *
            progress;


        const y =
            start.y +
            (end.y - start.y) *
            progress;


        fctx.beginPath();

        fctx.arc(
            x,
            y,
            2,
            0,
            Math.PI * 2
        );


        fctx.fillStyle =
            "rgba(110,235,255,.65)";

        fctx.shadowColor =
            "#22e8ff";

        fctx.shadowBlur = 10;

        fctx.fill();

        fctx.shadowBlur = 0;

    }


    /* ======================================================
       DRAW NODE
    ====================================================== */

    function drawFoodNode(
        node,
        index,
        time
    ) {

        const pos =
            foodNodePosition(node);


        const pulse =
            1 +
            Math.sin(
                time * .002 +
                index * 1.5
            ) * .08;


        const radius =
            30 * pulse;


        /* ------------------------------------------
           GLOW
        ------------------------------------------ */

        const glow =
            fctx.createRadialGradient(

                pos.x,
                pos.y,
                0,

                pos.x,
                pos.y,
                radius * 2.5

            );


        glow.addColorStop(
            0,
            "rgba(20,210,255,.22)"
        );

        glow.addColorStop(
            .45,
            "rgba(20,160,220,.08)"
        );

        glow.addColorStop(
            1,
            "rgba(20,160,220,0)"
        );


        fctx.beginPath();

        fctx.arc(
            pos.x,
            pos.y,
            radius * 2.5,
            0,
            Math.PI * 2
        );

        fctx.fillStyle =
            glow;

        fctx.fill();


        /* ------------------------------------------
           GLASS PANEL
        ------------------------------------------ */

        const isMobile = window.innerWidth <= 800;

const boxWidth = isMobile ? 105 : 145;
const boxHeight = isMobile ? 48 : 54;


        fctx.beginPath();

        fctx.roundRect(
            pos.x - boxWidth / 2,
            pos.y - boxHeight / 2,
            boxWidth,
            boxHeight,
            7
        );


        fctx.fillStyle =
            "rgba(3,18,30,.68)";

        fctx.fill();


        fctx.strokeStyle =
            "rgba(70,220,245,.48)";

        fctx.lineWidth = 1;

        fctx.shadowColor =
            "rgba(34,232,255,.45)";

        fctx.shadowBlur = 12;

        fctx.stroke();

        fctx.shadowBlur = 0;


        /* ------------------------------------------
           ICON
        ------------------------------------------ */

        drawFoodIcon(
            node.icon,
            pos.x,
            pos.y - 4
        );


        /* ------------------------------------------
           LABEL
        ------------------------------------------ */

        fctx.font =
            "500 11px Inter, sans-serif";

        fctx.textAlign =
            "center";

        fctx.textBaseline =
            "top";

        fctx.fillStyle =
            "#e2f2f7";


        fctx.fillText(
            node.name,
            pos.x,
            pos.y + 8
        );

    }


    /* ======================================================
       SIMPLE SYSTEM ICONS
    ====================================================== */

    function drawFoodIcon(
        type,
        x,
        y
    ) {

        fctx.save();

        fctx.translate(
            x,
            y
        );

        fctx.strokeStyle =
            "#63eaff";

        fctx.fillStyle =
            "#63eaff";

        fctx.lineWidth = 1.7;

        fctx.shadowColor =
            "#22e8ff";

        fctx.shadowBlur = 7;


        /* WEATHER */

        if (type === "weather") {

            fctx.beginPath();

            fctx.arc(
                0,
                2,
                9,
                Math.PI,
                0
            );

            fctx.stroke();

            fctx.beginPath();

            fctx.arc(
                -7,
                5,
                6,
                Math.PI,
                0
            );

            fctx.stroke();

            fctx.beginPath();

            fctx.moveTo(
                -8,
                8
            );

            fctx.lineTo(
                8,
                8
            );

            fctx.stroke();

        }


        /* SATELLITE */

        else if (type === "satellite") {

            fctx.beginPath();

            fctx.arc(
                0,
                0,
                5,
                0,
                Math.PI * 2
            );

            fctx.stroke();

            fctx.strokeRect(
                -16,
                -5,
                9,
                10
            );

            fctx.strokeRect(
                7,
                -5,
                9,
                10
            );

            fctx.beginPath();

            fctx.moveTo(
                -5,
                -5
            );

            fctx.lineTo(
                -12,
                -12
            );

            fctx.moveTo(
                5,
                5
            );

            fctx.lineTo(
                12,
                12
            );

            fctx.stroke();

        }


        /* FARMER */

        else if (type === "farmer") {

            fctx.beginPath();

            fctx.arc(
                0,
                -7,
                4,
                0,
                Math.PI * 2
            );

            fctx.stroke();

            fctx.beginPath();

            fctx.moveTo(
                -7,
                10
            );

            fctx.lineTo(
                0,
                0
            );

            fctx.lineTo(
                7,
                10
            );

            fctx.stroke();

            fctx.beginPath();

            fctx.moveTo(
                -10,
                2
            );

            fctx.lineTo(
                10,
                2
            );

            fctx.stroke();

        }


        /* MARKET */

        else {

            fctx.strokeRect(
                -12,
                -7,
                24,
                17
            );

            fctx.beginPath();

            fctx.moveTo(
                -12,
                -7
            );

            fctx.lineTo(
                -8,
                -13
            );

            fctx.lineTo(
                8,
                -13
            );

            fctx.lineTo(
                12,
                -7
            );

            fctx.stroke();

        }


        fctx.restore();

    }


    /* ======================================================
       SUBTLE FARM GRID
       
       Makes the aerial farmland feel like an actual
       agricultural landscape without overpowering it.
    ====================================================== */

    function drawFarmGrid(time) {

        fctx.save();

        fctx.globalAlpha = .12;

        fctx.strokeStyle =
            "#70eaff";

        fctx.lineWidth = 1;


        const spacing = 55;

        const drift =
            (time * .008) % spacing;


        for (
            let x = -fh;
            x < fw + fh;
            x += spacing
        ) {

            fctx.beginPath();

            fctx.moveTo(
                x + drift,
                0
            );

            fctx.lineTo(
                x - fh + drift,
                fh
            );

            fctx.stroke();

        }


        fctx.restore();

    }


    /* ======================================================
       ANIMATION
    ====================================================== */

    function animateFood(time) {

        fctx.clearRect(
            0,
            0,
            fw,
            fh
        );


        /* subtle field geometry */

        drawFarmGrid(time);


        /*
         * Connections:
         *
         * Weather ↔ Satellite
         * Weather ↔ Farmer
         * Satellite ↔ Market
         * Farmer ↔ Market
         */

        drawFoodConnection(
            foodNodes[0],
            foodNodes[1],
            0,
            time
        );

        drawFoodConnection(
            foodNodes[0],
            foodNodes[2],
            1,
            time
        );

        drawFoodConnection(
            foodNodes[1],
            foodNodes[3],
            2,
            time
        );

        drawFoodConnection(
            foodNodes[2],
            foodNodes[3],
            3,
            time
        );


        /* nodes */

        foodNodes.forEach(
            (node, index) => {

                drawFoodNode(
                    node,
                    index,
                    time
                );

            }
        );


        requestAnimationFrame(
            animateFood
        );

    }


    /* ======================================================
       START
    ====================================================== */

    resizeFood();

    window.addEventListener(
        "resize",
        resizeFood
    );

    requestAnimationFrame(
        animateFood
    );

}



/* ==========================================================
   RAYA — ONE PATTERN

   Phase 1:
   Systems appear independently.

   Phase 2:
   Everything connects.

   Phase 3:
   Connections disappear.

   Phase 4:
   Message appears.
========================================================== */


const patternCanvas =
    document.getElementById(
        "onePatternCanvas"
    );


if (patternCanvas) {

    const pctx =
        patternCanvas.getContext("2d");


    let pw;
    let ph;
    let pdpr;


    let startTime =
        performance.now();


    let messageShown =
        false;


    /* ======================================================
       SYSTEMS
    ====================================================== */

    const patternNodes = [

        {
            name: "Climate",
            x: .50,
            y: .20
        },

        {
            name: "Energy",
            x: .25,
            y: .34
        },

        {
            name: "Water",
            x: .75,
            y: .34
        },

        {
            name: "Food",
            x: .20,
            y: .62
        },

        {
            name: "Health",
            x: .80,
            y: .62
        },

        {
            name: "Economy",
            x: .35,
            y: .82
        },

        {
            name: "Population",
            x: .65,
            y: .82
        },

        {
            name: "Environment",
            x: .50,
            y: .52
        }

    ];


    /* ======================================================
       CONNECTION MAP
    ====================================================== */

    const patternConnections = [

        [0, 1],
        [0, 2],

        [0, 7],

        [1, 3],
        [1, 5],

        [2, 4],
        [2, 6],

        [3, 5],
        [3, 7],

        [4, 6],
        [4, 7],

        [5, 6],

        [5, 7],
        [6, 7]

    ];


    /* ======================================================
       TIMING
    ====================================================== */

    /*
     * 0–3 sec
     * Nodes appear
     *
     * 3–8 sec
     * Connections build
     *
     * 8–10 sec
     * Network stays connected
     *
     * 10–11 sec
     * Everything disappears
     *
     * 11.5 sec
     * Message appears
     */

    const NODE_PHASE =
        3000;

    const CONNECT_PHASE =
        5000;

    const HOLD_PHASE =
        2000;

    const COLLAPSE_PHASE =
        1000;


    /* ======================================================
       RESIZE
    ====================================================== */

    function resizePattern() {

        pdpr =
            Math.min(
                window.devicePixelRatio || 1,
                2
            );


        pw =
            patternCanvas
                .parentElement
                .clientWidth;


        ph =
            patternCanvas
                .parentElement
                .clientHeight;


        patternCanvas.width =
            pw * pdpr;


        patternCanvas.height =
            ph * pdpr;


        patternCanvas.style.width =
            pw + "px";


        patternCanvas.style.height =
            ph + "px";


        pctx.setTransform(
            pdpr,
            0,
            0,
            pdpr,
            0,
            0
        );

    }


    /* ======================================================
       NODE POSITION
    ====================================================== */

    function getPatternNode(
        node
    ) {

        return {

            x:
                node.x * pw,

            y:
                node.y * ph

        };

    }


    /* ======================================================
       EASING
    ====================================================== */

    function easeOut(
        value
    ) {

        return 1 -
            Math.pow(
                1 - value,
                3
            );

    }


    function easeIn(
        value
    ) {

        return value * value;

    }


    /* ======================================================
       DRAW NODE
    ====================================================== */

    function drawPatternNode(
        node,
        index,
        visibility,
        time
    ) {

        if (
            visibility <= 0
        )
            return;


        const pos =
            getPatternNode(node);


        /*
         * Tiny natural movement.
         */

        const floatX =
            Math.sin(
                time * .0007 +
                index * 1.8
            ) * 3;


        const floatY =
            Math.cos(
                time * .0008 +
                index
            ) * 3;


        const x =
            pos.x +
            floatX;


        const y =
            pos.y +
            floatY;


        const pulse =
            1 +
            Math.sin(
                time * .002 +
                index
            ) * .08;


        /* ------------------------------------------
           GLOW
        ------------------------------------------ */

        const glow =
            pctx.createRadialGradient(

                x,
                y,
                0,

                x,
                y,
                34

            );


        glow.addColorStop(
            0,
            `rgba(
                45,
                225,
                255,
                ${.18 * visibility}
            )`
        );


        glow.addColorStop(
            1,
            "rgba(45,225,255,0)"
        );


        pctx.beginPath();

        pctx.arc(
            x,
            y,
            34,
            0,
            Math.PI * 2
        );


        pctx.fillStyle =
            glow;

        pctx.fill();


        /* ------------------------------------------
           CORE
        ------------------------------------------ */

        pctx.beginPath();

        pctx.arc(
            x,
            y,
            5 * pulse,
            0,
            Math.PI * 2
        );


        pctx.fillStyle =
            `rgba(
                105,
                240,
                255,
                ${visibility}
            )`;


        pctx.shadowColor =
            "#22e8ff";


        pctx.shadowBlur =
            18;


        pctx.fill();


        pctx.shadowBlur = 0;


        /* ------------------------------------------
           LABEL
        ------------------------------------------ */

        pctx.font =
            "500 12px Inter, sans-serif";


        pctx.textAlign =
            "center";


        pctx.textBaseline =
            "top";


        pctx.fillStyle =
            `rgba(
                220,
                239,
                247,
                ${visibility * .9}
            )`;


        pctx.fillText(
            node.name,
            x,
            y + 14
        );

    }


    /* ======================================================
       DRAW CONNECTION
    ====================================================== */

    function drawPatternConnection(
        connection,
        progress,
        time
    ) {

        if (
            progress <= 0
        )
            return;


        const start =
            getPatternNode(
                patternNodes[
                    connection[0]
                ]
            );


        const end =
            getPatternNode(
                patternNodes[
                    connection[1]
                ]
            );


        const current =
            easeOut(
                Math.min(
                    progress,
                    1
                )
            );


        const x2 =
            start.x +
            (end.x - start.x) *
            current;


        const y2 =
            start.y +
            (end.y - start.y) *
            current;


        /* ------------------------------------------
           CONNECTION
        ------------------------------------------ */

        pctx.beginPath();


        pctx.moveTo(
            start.x,
            start.y
        );


        pctx.lineTo(
            x2,
            y2
        );


        pctx.strokeStyle =
            `rgba(
                65,
                220,
                255,
                ${.42 * current}
            )`;


        pctx.lineWidth =
            1.2;


        pctx.shadowColor =
            "rgba(34,232,255,.45)";


        pctx.shadowBlur =
            7;


        pctx.stroke();


        pctx.shadowBlur = 0;


        /* ------------------------------------------
           TRAVELLING SIGNAL
        ------------------------------------------ */

        if (
            current > .15 &&
            current < .98
        ) {

            const signalX =
                start.x +
                (end.x - start.x) *
                current;


            const signalY =
                start.y +
                (end.y - start.y) *
                current;


            pctx.beginPath();


            pctx.arc(
                signalX,
                signalY,
                2.3,
                0,
                Math.PI * 2
            );


            pctx.fillStyle =
                "#8af7ff";


            pctx.shadowColor =
                "#22e8ff";


            pctx.shadowBlur =
                15;


            pctx.fill();


            pctx.shadowBlur = 0;

        }

    }


    /* ======================================================
       MAIN ANIMATION
    ====================================================== */

    function animatePattern(
        time
    ) {

        const elapsed =
            time -
            startTime;


        pctx.clearRect(
            0,
            0,
            pw,
            ph
        );


        /* ==================================================
           PHASE 1 — NODES APPEAR
        ================================================== */

        let nodeVisibility = 1;


        if (
            elapsed < NODE_PHASE
        ) {

            /*
             * Nodes appear sequentially.
             */

            patternNodes.forEach(
                (node, index) => {

                    const delay =
                        index *
                        180;


                    const local =
                        Math.max(
                            0,
                            Math.min(
                                1,
                                (
                                    elapsed -
                                    delay
                                ) / 600
                            )
                        );


                    drawPatternNode(
                        node,
                        index,
                        easeOut(local),
                        time
                    );

                }
            );

        }


        /* ==================================================
           PHASE 2 — CONNECTIONS BUILD
        ================================================== */

        else if (
            elapsed <
            NODE_PHASE +
            CONNECT_PHASE
        ) {

            patternNodes.forEach(
                (node, index) => {

                    drawPatternNode(
                        node,
                        index,
                        1,
                        time
                    );

                }
            );


            const connectionElapsed =
                elapsed -
                NODE_PHASE;


            const connectionStep =
                CONNECT_PHASE /
                patternConnections.length;


            patternConnections.forEach(
                (connection, index) => {

                    const startTime =
                        index *
                        connectionStep *
                        .72;


                    const progress =
                        Math.max(
                            0,
                            Math.min(
                                1,
                                (
                                    connectionElapsed -
                                    startTime
                                ) /
                                connectionStep
                            )
                        );


                    drawPatternConnection(
                        connection,
                        progress,
                        time
                    );

                }
            );

        }


        /* ==================================================
           PHASE 3 — FULL NETWORK
        ================================================== */

        else if (
            elapsed <
            NODE_PHASE +
            CONNECT_PHASE +
            HOLD_PHASE
        ) {

            patternNodes.forEach(
                (node, index) => {

                    drawPatternNode(
                        node,
                        index,
                        1,
                        time
                    );

                }
            );


            patternConnections.forEach(
                connection => {

                    drawPatternConnection(
                        connection,
                        1,
                        time
                    );

                }
            );

        }


        /* ==================================================
           PHASE 4 — SUDDEN COLLAPSE
        ================================================== */

        else if (
            elapsed <
            NODE_PHASE +
            CONNECT_PHASE +
            HOLD_PHASE +
            COLLAPSE_PHASE
        ) {

            const collapseElapsed =
                elapsed -
                (
                    NODE_PHASE +
                    CONNECT_PHASE +
                    HOLD_PHASE
                );


            /*
             * Connections disappear much faster
             * than they appeared.
             */

            const connectionOpacity =
                1 -
                easeIn(
                    collapseElapsed /
                    COLLAPSE_PHASE
                );


            patternNodes.forEach(
                (node, index) => {

                    drawPatternNode(
                        node,
                        index,
                        1,
                        time
                    );

                }
            );


            patternConnections.forEach(
                connection => {

                    drawPatternConnection(
                        connection,
                        connectionOpacity,
                        time
                    );

                }
            );

        }


        /* ==================================================
           PHASE 5 — ISOLATED SYSTEMS
        ================================================== */

        else {

            patternNodes.forEach(
                (node, index) => {

                    drawPatternNode(
                        node,
                        index,
                        1,
                        time
                    );

                }
            );


            /*
             * Reveal message once.
             */

            if (
                !messageShown
            ) {

                messageShown =
                    true;


                const message =
                    document.querySelector(
                        ".one-pattern-message"
                    );


                if (
                    message
                ) {

                    message.classList.add(
                        "show"
                    );

                }

            }

        }


        requestAnimationFrame(
            animatePattern
        );

    }


    /* ======================================================
       START
    ====================================================== */

    resizePattern();


    window.addEventListener(
        "resize",
        resizePattern
    );


    requestAnimationFrame(
        animatePattern
    );

}



/* ==========================================================
   RAYA — RESOLUTION

   Phase 1:
   Systems appear

   Phase 2:
   Systems move toward RAYA

   Phase 3:
   RAYA core appears

   Phase 4:
   Connections form

   Phase 5:
   Intelligence layer stabilizes
========================================================== */

const rayaCanvas =
    document.getElementById("rayaResolutionCanvas");

if (rayaCanvas) {

    const rctx =
        rayaCanvas.getContext("2d");

    let rw = 0;
    let rh = 0;
    let rdpr = 1;

    const startTime =
        performance.now();


    /* ======================================================
       SAME SYSTEMS FROM SECTION 7
    ====================================================== */

    const rayaNodes = [

        {
            name: "Climate",
            x: .50,
            y: .18
        },

        {
            name: "Energy",
            x: .26,
            y: .31
        },

        {
            name: "Water",
            x: .74,
            y: .31
        },

        {
            name: "Food",
            x: .20,
            y: .58
        },

        {
            name: "Health",
            x: .80,
            y: .58
        },

        {
            name: "Economy",
            x: .31,
            y: .79
        },

        {
            name: "Population",
            x: .69,
            y: .79
        },

        {
            name: "Environment",
            x: .50,
            y: .57
        }

    ];


    /* ======================================================
       RESIZE
    ====================================================== */

    function resizeRaya() {

        rdpr =
            Math.min(
                window.devicePixelRatio || 1,
                2
            );

        rw =
            rayaCanvas.parentElement.clientWidth;

        rh =
            rayaCanvas.parentElement.clientHeight;

        rayaCanvas.width =
            rw * rdpr;

        rayaCanvas.height =
            rh * rdpr;

        rayaCanvas.style.width =
            rw + "px";

        rayaCanvas.style.height =
            rh + "px";

        rctx.setTransform(
            rdpr,
            0,
            0,
            rdpr,
            0,
            0
        );

    }


    /* ======================================================
       EASING
    ====================================================== */

    function easeOut(t) {

        return 1 -
            Math.pow(
                1 - t,
                3
            );

    }


    /* ======================================================
       NODE POSITION
    ====================================================== */

    function getNodePosition(
        node
    ) {

        return {

            x:
                node.x * rw,

            y:
                node.y * rh

        };

    }


    /* ======================================================
       DRAW NODE
    ====================================================== */

    function drawNode(
        node,
        index,
        progress,
        time,
        converge
    ) {

        if (progress <= 0)
            return;


        const original =
            getNodePosition(node);


        /*
         * During convergence the nodes
         * move slightly toward the centre.
         */

        const centreX =
            rw * .5;

        const centreY =
            rh * .5;


        const move =
            easeOut(converge);


        const x =
            original.x +
            (centreX - original.x)
            * move;


        const y =
            original.y +
            (centreY - original.y)
            * move;


        /*
         * Gentle floating after connection.
         */

        const floatX =
            Math.sin(
                time * .0007 +
                index
            ) * 2.5 *
            (1 - move);


        const floatY =
            Math.cos(
                time * .0008 +
                index * 1.3
            ) * 2.5 *
            (1 - move);


        const finalX =
            x + floatX;

        const finalY =
            y + floatY;


        /* ==================================================
           GLOW
        ================================================== */

        const glow =
            rctx.createRadialGradient(

                finalX,
                finalY,
                0,

                finalX,
                finalY,
                32

            );


        glow.addColorStop(
            0,
            `rgba(
                50,
                225,
                255,
                ${.20 * progress}
            )`
        );


        glow.addColorStop(
            1,
            "rgba(50,225,255,0)"
        );


        rctx.beginPath();

        rctx.arc(
            finalX,
            finalY,
            32,
            0,
            Math.PI * 2
        );

        rctx.fillStyle =
            glow;

        rctx.fill();


        /* ==================================================
           NODE
        ================================================== */

        rctx.beginPath();

        rctx.arc(
            finalX,
            finalY,
            5,
            0,
            Math.PI * 2
        );


        rctx.fillStyle =
            `rgba(
                110,
                240,
                255,
                ${progress}
            )`;


        rctx.shadowColor =
            "#22e8ff";

        rctx.shadowBlur =
            18;

        rctx.fill();

        rctx.shadowBlur = 0;


        /* ==================================================
           LABEL
        ================================================== */

        rctx.font =
            "500 12px Inter, sans-serif";

        rctx.textAlign =
            "center";

        rctx.textBaseline =
            "top";

        rctx.fillStyle =
            `rgba(
                220,
                240,
                247,
                ${.9 * progress}
            )`;


        rctx.fillText(
            node.name,
            finalX,
            finalY + 13
        );

    }


    /* ======================================================
       DRAW CONNECTION
    ====================================================== */

    function drawConnection(
        node,
        progress,
        time,
        converge
    ) {

        if (progress <= 0)
            return;


        const original =
            getNodePosition(node);


        const centreX =
            rw * .5;

        const centreY =
            rh * .5;


        const move =
            easeOut(converge);


        const startX =
            original.x +
            (centreX - original.x)
            * move;


        const startY =
            original.y +
            (centreY - original.y)
            * move;


        /*
         * Connection begins only
         * after nodes start converging.
         */

        const current =
            easeOut(
                Math.min(
                    progress,
                    1
                )
            );


        const endX =
            startX +
            (centreX - startX)
            * current;


        const endY =
            startY +
            (centreY - startY)
            * current;


        /* ==================================================
           MAIN LINE
        ================================================== */

        rctx.beginPath();

        rctx.moveTo(
            startX,
            startY
        );

        rctx.lineTo(
            endX,
            endY
        );


        rctx.strokeStyle =
            `rgba(
                70,
                230,
                255,
                ${.72 * current}
            )`;


        rctx.lineWidth =
            1.3;


        rctx.shadowColor =
            "rgba(34,232,255,.65)";

        rctx.shadowBlur =
            9;

        rctx.stroke();

        rctx.shadowBlur = 0;


        /* ==================================================
           MOVING LIGHT
        ================================================== */

        if (
            current > .05 &&
            current < .98
        ) {

            const pulse =
                (
                    time * .00035 +
                    node.x * 2
                ) % 1;


            const px =
                startX +
                (endX - startX) *
                pulse;


            const py =
                startY +
                (endY - startY) *
                pulse;


            rctx.beginPath();

            rctx.arc(
                px,
                py,
                2.5,
                0,
                Math.PI * 2
            );


            rctx.fillStyle =
                "#b7fbff";

            rctx.shadowColor =
                "#22e8ff";

            rctx.shadowBlur =
                18;

            rctx.fill();

            rctx.shadowBlur = 0;

        }

    }


    /* ======================================================
       CENTRAL RAYA CORE
    ====================================================== */

    function drawCore(
        progress,
        time
    ) {

        if (progress <= 0)
            return;


        const cx =
            rw * .5;

        const cy =
            rh * .5;


        const pulse =
            1 +
            Math.sin(
                time * .002
            ) * .08;


        const radius =
            34 *
            easeOut(progress) *
            pulse;


        /* ==================================================
           LARGE ATMOSPHERIC GLOW
        ================================================== */

        const glow =
            rctx.createRadialGradient(

                cx,
                cy,
                0,

                cx,
                cy,
                radius * 6

            );


        glow.addColorStop(
            0,
            "rgba(100,245,255,.42)"
        );

        glow.addColorStop(
            .25,
            "rgba(40,210,255,.20)"
        );

        glow.addColorStop(
            .60,
            "rgba(20,120,220,.07)"
        );

        glow.addColorStop(
            1,
            "rgba(0,0,0,0)"
        );


        rctx.beginPath();

        rctx.arc(
            cx,
            cy,
            radius * 6,
            0,
            Math.PI * 2
        );

        rctx.fillStyle =
            glow;

        rctx.fill();


        /* ==================================================
           CORE
        ================================================== */

        rctx.beginPath();

        rctx.arc(
            cx,
            cy,
            radius,
            0,
            Math.PI * 2
        );


        rctx.fillStyle =
            "rgba(8,45,65,.96)";


        rctx.strokeStyle =
            "rgba(125,248,255,.98)";


        rctx.lineWidth =
            1.5;


        rctx.shadowColor =
            "#22e8ff";

        rctx.shadowBlur =
            35;


        rctx.fill();

        rctx.stroke();

        rctx.shadowBlur = 0;


        /* ==================================================
           RAYA INSIDE CORE
        ================================================== */

        if (progress > .65) {

            rctx.font =
                "600 11px Inter, sans-serif";

            rctx.textAlign =
                "center";

            rctx.textBaseline =
                "middle";

            rctx.fillStyle =
                "#eaffff";


            rctx.fillText(
                "RAYA",
                cx,
                cy
            );

        }

    }


    /* ======================================================
       MAIN ANIMATION
    ====================================================== */

    function animateRaya(
        time
    ) {

        const elapsed =
            time -
            startTime;


        rctx.clearRect(
            0,
            0,
            rw,
            rh
        );


        /* ==================================================
           PHASE 1 — SYSTEMS APPEAR
           0 → 2 sec
        ================================================== */

        const nodePhase =
            Math.min(
                1,
                elapsed / 2000
            );


        rayaNodes.forEach(
            (node, index) => {

                const delay =
                    index * 120;


                const progress =
                    Math.max(
                        0,
                        Math.min(
                            1,
                            (
                                elapsed -
                                delay
                            ) / 650
                        )
                    );


                drawNode(
                    node,
                    index,
                    easeOut(progress),
                    time,
                    0
                );

            }
        );


        /* ==================================================
           PHASE 2 — MOVE TOWARD CENTRE
           2 → 3.5 sec
        ================================================== */

        const convergeProgress =
            Math.max(
                0,
                Math.min(
                    1,
                    (
                        elapsed -
                        2000
                    ) / 1500
                )
            );


        /* ==================================================
           PHASE 3 — RAYA CORE
           3 → 4.5 sec
        ================================================== */

        const coreProgress =
            Math.max(
                0,
                Math.min(
                    1,
                    (
                        elapsed -
                        3000
                    ) / 1500
                )
            );


        /* ==================================================
           DRAW MOVING NODES
        ================================================== */

        rayaNodes.forEach(
            (node, index) => {

                drawNode(
                    node,
                    index,
                    1,
                    time,
                    convergeProgress
                );

            }
        );


        /* ==================================================
           PHASE 4 — CONNECTIONS
           3.8 → 6 sec
        ================================================== */

        const connectionProgress =
            Math.max(
                0,
                Math.min(
                    1,
                    (
                        elapsed -
                        3800
                    ) / 2200
                )
            );


        rayaNodes.forEach(
            (node, index) => {

                const delay =
                    index * .07;


                drawConnection(
                    node,

                    Math.max(
                        0,
                        connectionProgress -
                        delay
                    ),

                    time,

                    convergeProgress
                );

            }
        );


        /* ==================================================
           CORE
        ================================================== */

        drawCore(
            coreProgress,
            time
        );


        /* ==================================================
           CONTINUE
        ================================================== */

        requestAnimationFrame(
            animateRaya
        );

    }


    /* ======================================================
       START
    ====================================================== */

    resizeRaya();

    window.addEventListener(
        "resize",
        resizeRaya
    );

    requestAnimationFrame(
        animateRaya
    );

}


/* ==========================================================
   RAYA — SOFT SECTION ENTRY
========================================================== */

const storySections = document.querySelectorAll(
    ".integrated-earth, " +
    ".human-fragmentation, " +
    ".climate-cinematic, " +
    ".energy-network, " +
    ".food-cinematic, " +
    ".one-pattern, " +
    ".raya-resolution"
);


const storyObserver =
    new IntersectionObserver(
        entries => {

            entries.forEach(entry => {

                if (entry.isIntersecting) {

                    entry.target.classList.add(
                        "story-visible"
                    );

                }

            });

        },
        {
            threshold: 0.12
        }
    );


storySections.forEach(section => {

    storyObserver.observe(section);

});

