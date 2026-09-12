/* ==========================================
   RAYA TYPE-1 VISION
========================================== */

const slides = document.getElementById("slides");
const slideList = document.querySelectorAll(".slide");

const dots = document.querySelectorAll(".dot");

const nextBtn = document.getElementById("nextSlide");
const prevBtn = document.getElementById("prevSlide");

const continueBtn = document.querySelector(".continue");

const planetaryBg =
    document.getElementById("planetary-bg");

let current = 0;

const total = slideList.length;

let locked = false;

/* ==========================================
GO TO SLIDE
========================================== */

function goTo(index){

    if(index<0) index=0;

    if(index>=total) index=total-1;

    current=index;

    if (planetaryBg) {

    const showPlanetaryBackground =
        current >= 1 && current <= 4;

    planetaryBg.classList.toggle(
        "active",
        showPlanetaryBackground
    );

    document.body.classList.toggle(
        "planetary-mode",
        showPlanetaryBackground
    );

}

    slides.style.transform=
    `translateX(-${current*100}vw)`;

    slideList.forEach(slide=>{

        slide.classList.remove("active");

    });

    slideList[current].classList.add("active");

    /* ==========================================
   REPLAY ROADMAP SEQUENCE
========================================== */

if (slideList[current].classList.contains("roadmap")) {

    const roadmap = slideList[current];

    roadmap.classList.remove("roadmap-run");

    void roadmap.offsetWidth;

    roadmap.classList.add("roadmap-run");
}

/* ==========================================
   REPLAY CINEMATIC FINALE
========================================== */

if (
    slideList[current]
    .classList.contains("cinematic-final")
) {

    const finalSlide =
        slideList[current];


    finalSlide.classList.remove(
        "final-run"
    );


    if(window.resetFinalEarth){

        window.resetFinalEarth();

    }


    void finalSlide.offsetWidth;


    finalSlide.classList.add(
        "final-run"
    );

}
    dots.forEach(dot=>{

        dot.classList.remove("active");

    });

    dots[current].classList.add("active");

    prevBtn.style.opacity=current===0?.35:1;

    nextBtn.style.opacity=current===total-1?.35:1;

}



/* ==========================================
NEXT
========================================== */

function nextSlide(){

    if(locked)return;

    locked=true;

    goTo(current+1);

    setTimeout(()=>{

        locked=false;

    },900);

}

/* ==========================================
PREVIOUS
========================================== */

function previousSlide(){

    if(locked)return;

    locked=true;

    goTo(current-1);

    setTimeout(()=>{

        locked=false;

    },900);

}

/* ==========================================
BUTTONS
========================================== */

nextBtn.onclick=nextSlide;

prevBtn.onclick=previousSlide;

if(continueBtn){

    continueBtn.onclick=nextSlide;

}

/* ==========================================
DOTS
========================================== */

dots.forEach((dot,index)=>{

    dot.onclick=()=>{

        goTo(index);

    }

});

/* ==========================================
KEYBOARD
========================================== */

document.addEventListener("keydown",e=>{

    if(e.key==="ArrowRight"){

        nextSlide();

    }

    if(e.key==="ArrowLeft"){

        previousSlide();

    }

});

/* ==========================================
MOUSE WHEEL
========================================== */

window.addEventListener("wheel", e => {

    // Last slide + scrolling down = allow page to reach footer
    if(current === slideList.length - 1 && e.deltaY > 0){
        return;
    }

    // First slide + scrolling up = allow normal page behavior
    if(current === 0 && e.deltaY < 0){
        return;
    }

    e.preventDefault();

    if(locked) return;

    if(e.deltaY > 0 && current < slideList.length - 1){
        goTo(current + 1);
    }
    else if(e.deltaY < 0 && current > 0){
        goTo(current - 1);
    }

},{passive:false});

/* ==========================================
TOUCH
========================================== */

let touchStart=0;

window.addEventListener("touchstart",e=>{

    touchStart=e.touches[0].clientX;

});

window.addEventListener("touchend",e=>{

    let diff=touchStart-e.changedTouches[0].clientX;

    if(Math.abs(diff)<60)return;

    if(diff>0){

        nextSlide();

    }else{

        previousSlide();

    }

});

/* ==========================================
AUTO PEEK
========================================== */

setTimeout(()=>{

    slides.style.transition="transform .9s ease";

    slides.style.transform="translateX(-18vw)";

    setTimeout(()=>{

        slides.style.transform="translateX(0)";

        setTimeout(()=>{

            slides.style.transition="transform 1s cubic-bezier(.77,0,.18,1)";

        },1000);

    },1200);

},1800);

/* ==========================================
MOUSE GLOW
========================================== */

const glow=document.querySelector(".mouse-glow");

document.addEventListener("mousemove",e=>{

    glow.style.left=e.clientX+"px";

    glow.style.top=e.clientY+"px";

});

/* ==========================================
PARTICLES
========================================== */

const canvas=document.getElementById("particles");

const ctx=canvas.getContext("2d");

function resize(){

    canvas.width=window.innerWidth;

    canvas.height=window.innerHeight;

}

resize();

window.addEventListener("resize",resize);

const particles=[];

for(let i=0;i<140;i++){

    particles.push({

        x:Math.random()*canvas.width,

        y:Math.random()*canvas.height,

        r:Math.random()*2.5,

        dx:(Math.random()-.5)*0.25,

        dy:(Math.random()-.5)*0.25

    });

}

function animateParticles(){

    ctx.clearRect(0,0,canvas.width,canvas.height);

    particles.forEach(p=>{

        p.x+=p.dx;

        p.y+=p.dy;

        if(p.x<0)p.x=canvas.width;

        if(p.x>canvas.width)p.x=0;

        if(p.y<0)p.y=canvas.height;

        if(p.y>canvas.height)p.y=0;

        ctx.beginPath();

        ctx.arc(p.x,p.y,p.r,0,Math.PI*2);

        ctx.fillStyle="rgba(255,255,255,.75)";

        ctx.fill();

    });

    requestAnimationFrame(animateParticles);

}

animateParticles();

/* ==========================================
INITIALIZE
========================================== */

goTo(0);
/* ==========================================================
   RAYA PLANETARY INTELLIGENCE VISUAL
========================================================== */

const planetCanvas = document.getElementById("planetCanvas");

if (planetCanvas) {

    const pctx = planetCanvas.getContext("2d");

    const DPR = window.devicePixelRatio || 1;

    const SIZE = 570;

    planetCanvas.width = SIZE * DPR;
    planetCanvas.height = SIZE * DPR;

    pctx.scale(DPR, DPR);

    const cx = SIZE / 2;
    const cy = SIZE / 2;

    const earthRadius = 175;

    let rotation = 0;
    let cloudRotation = 0;
    let networkRotation = 0;


    /* ======================================================
       EARTH DATA POINTS
    ====================================================== */

    const continents = [];

    for (let i = 0; i < 240; i++) {

        continents.push({

            lat: (Math.random() - .5) * Math.PI,

            lon: Math.random() * Math.PI * 2,

            size: Math.random() * 2.5 + .7,

            brightness: Math.random()

        });

    }


    /* ======================================================
       CLOUD PARTICLES
    ====================================================== */

    const clouds = [];

    for (let i = 0; i < 100; i++) {

        clouds.push({

            lat: (Math.random() - .5) * Math.PI,

            lon: Math.random() * Math.PI * 2,

            size: Math.random() * 7 + 3

        });

    }


    /* ======================================================
       NETWORK NODES
    ====================================================== */

    const nodes = [

        { lat: .62, lon: .20 },
        { lat: .35, lon: 1.15 },
        { lat: -.18, lon: 1.85 },
        { lat: .05, lon: 2.75 },
        { lat: -.55, lon: 3.60 },
        { lat: .45, lon: 4.25 },
        { lat: -.25, lon: 5.20 },
        { lat: .75, lon: 5.75 }

    ];


    /* ======================================================
       SATELLITES
    ====================================================== */

    // const satellites = [

    //     {
    //         radius: 235,
    //         speed: .006,
    //         angle: 0,
    //         tilt: .34
    //     },

    //     {
    //         radius: 255,
    //         speed: -.004,
    //         angle: 2,
    //         tilt: -.25
    //     },

    //     {
    //         radius: 220,
    //         speed: .005,
    //         angle: 4,
    //         tilt: .60
    //     }

    // ];
    const satellites = [
    {
        radius: 235,
        speed: .0025,
        angle: 0,
        tilt: .34
    },
    {
        radius: 255,
        speed: -.0018,
        angle: 2,
        tilt: -.25
    },
    {
        radius: 220,
        speed: .0022,
        angle: 4,
        tilt: .60
    }
];


    /* ======================================================
       3D SPHERE PROJECTION
    ====================================================== */

    function project(lat, lon, radius, rot = 0) {

        const longitude = lon + rot;

        const x =
            Math.cos(lat) *
            Math.sin(longitude);

        const y =
            Math.sin(lat);

        const z =
            Math.cos(lat) *
            Math.cos(longitude);

        return {

            x: cx + x * radius,

            y: cy - y * radius,

            z: z

        };

    }


    /* ======================================================
       EARTH
    ====================================================== */

    function drawEarth() {

        pctx.save();

        pctx.beginPath();

        pctx.arc(
            cx,
            cy,
            earthRadius,
            0,
            Math.PI * 2
        );

        pctx.clip();


        /* Ocean */

        const ocean = pctx.createRadialGradient(

            cx - 65,
            cy - 70,
            20,

            cx,
            cy,
            earthRadius

        );

        ocean.addColorStop(
            0,
            "#1268a1"
        );

        ocean.addColorStop(
            .38,
            "#073d69"
        );

        ocean.addColorStop(
            .75,
            "#031c38"
        );

        ocean.addColorStop(
            1,
            "#010914"
        );

        pctx.fillStyle = ocean;

        pctx.fillRect(
            cx - earthRadius,
            cy - earthRadius,
            earthRadius * 2,
            earthRadius * 2
        );


        /* Night-side shadow */

        const shadow =
            pctx.createLinearGradient(

                cx - earthRadius,
                cy,

                cx + earthRadius,
                cy

            );

        shadow.addColorStop(
            0,
            "rgba(0,0,0,.08)"
        );

        shadow.addColorStop(
            .55,
            "rgba(0,0,0,.15)"
        );

        shadow.addColorStop(
            1,
            "rgba(0,0,0,.88)"
        );

        pctx.fillStyle = shadow;

        pctx.fillRect(
            cx - earthRadius,
            cy - earthRadius,
            earthRadius * 2,
            earthRadius * 2
        );


        /* Surface points */

        continents.forEach(point => {

            const pos =
                project(
                    point.lat,
                    point.lon,
                    earthRadius - 4,
                    rotation
                );

            if (pos.z <= 0)
                return;

            const opacity =
                .15 +
                pos.z * .55;

            pctx.beginPath();

            pctx.arc(
                pos.x,
                pos.y,
                point.size,
                0,
                Math.PI * 2
            );

            if (point.brightness > .72) {

                pctx.fillStyle =
                    `rgba(120,230,180,${opacity})`;

            } else {

                pctx.fillStyle =
                    `rgba(40,125,90,${opacity})`;

            }

            pctx.fill();

        });


        /* Clouds */

        clouds.forEach(cloud => {

            const pos =
                project(
                    cloud.lat,
                    cloud.lon,
                    earthRadius,
                    cloudRotation
                );

            if (pos.z <= 0)
                return;

            pctx.beginPath();

            pctx.arc(
                pos.x,
                pos.y,
                cloud.size * pos.z,
                0,
                Math.PI * 2
            );

            pctx.fillStyle =
                `rgba(255,255,255,${.03 + pos.z * .11})`;

            pctx.fill();

        });


        pctx.restore();


        /* Planet outline */

        pctx.beginPath();

        pctx.arc(
            cx,
            cy,
            earthRadius,
            0,
            Math.PI * 2
        );

        pctx.strokeStyle =
            "rgba(70,220,255,.55)";

        pctx.lineWidth = 1.4;

        pctx.stroke();

    }


    /* ======================================================
       PLANETARY NETWORK
    ====================================================== */

    function drawNetwork() {

        const projected =
            nodes.map(node =>
                project(
                    node.lat,
                    node.lon,
                    earthRadius + 3,
                    rotation + networkRotation
                )
            );


        projected.forEach(
            (point, index) => {

                if (point.z <= 0)
                    return;

                const next =
                    projected[
                        (index + 2) %
                        projected.length
                    ];

                if (next.z > 0) {

                    pctx.beginPath();

                    pctx.moveTo(
                        point.x,
                        point.y
                    );

                    const controlX =
                        (point.x + next.x) / 2;

                    const controlY =
                        (point.y + next.y) / 2 - 35;

                    pctx.quadraticCurveTo(

                        controlX,
                        controlY,

                        next.x,
                        next.y

                    );

                    pctx.strokeStyle =
                        `rgba(34,232,255,${.15 + point.z * .45})`;

                    pctx.lineWidth = 1;

                    pctx.stroke();

                }


                /* Node */

                pctx.beginPath();

                pctx.arc(
                    point.x,
                    point.y,
                    2.5,
                    0,
                    Math.PI * 2
                );

                pctx.fillStyle =
                    "#6ff5ff";

                pctx.shadowColor =
                    "#22e8ff";

                pctx.shadowBlur = 12;

                pctx.fill();

                pctx.shadowBlur = 0;

            }
        );

    }


    /* ======================================================
       ORBIT PATHS
    ====================================================== */

    function drawOrbitPaths() {

        pctx.save();

        pctx.translate(cx, cy);

        pctx.strokeStyle =
            "rgba(100,220,255,.12)";

        pctx.lineWidth = 1;


        /* Orbit 1 */

        pctx.beginPath();

        pctx.ellipse(
            0,
            0,
            240,
            95,
            .32,
            0,
            Math.PI * 2
        );

        pctx.stroke();


        /* Orbit 2 */

        pctx.beginPath();

        pctx.ellipse(
            0,
            0,
            260,
            110,
            -.48,
            0,
            Math.PI * 2
        );

        pctx.stroke();


        pctx.restore();

    }


    /* ======================================================
       SATELLITES
    ====================================================== */

    function drawSatellites() {

        satellites.forEach(sat => {

            sat.angle += sat.speed;

            const x =
                cx +
                Math.cos(sat.angle) *
                sat.radius;

            const y =
                cy +
                Math.sin(sat.angle) *
                sat.radius *
                sat.tilt;


            /* satellite glow */

            pctx.beginPath();

            pctx.arc(
                x,
                y,
                3,
                0,
                Math.PI * 2
            );

            pctx.fillStyle =
                "#d9fbff";

            pctx.shadowColor =
                "#22e8ff";

            pctx.shadowBlur = 14;

            pctx.fill();

            pctx.shadowBlur = 0;


            /* satellite body */

            pctx.fillStyle =
                "#9ed8df";

            pctx.fillRect(
                x - 4,
                y - 2,
                8,
                4
            );


            /* solar panels */

            pctx.fillStyle =
                "rgba(40,180,220,.75)";

            pctx.fillRect(
                x - 11,
                y - 1,
                6,
                2
            );

            pctx.fillRect(
                x + 5,
                y - 1,
                6,
                2
            );

        });

    }


    /* ======================================================
       DATA ORBIT PARTICLES
    ====================================================== */

    function drawDataOrbit() {

        const time =
            Date.now() * .001;

        for (let i = 0; i < 14; i++) {

            const angle =
                time * .25 +
                i *
                (Math.PI * 2 / 14);

            const x =
                cx +
                Math.cos(angle) *
                215;

            const y =
                cy +
                Math.sin(angle) *
                72;

            pctx.beginPath();

            pctx.arc(
                x,
                y,
                1.5,
                0,
                Math.PI * 2
            );

            pctx.fillStyle =
                "rgba(90,245,255,.7)";

            pctx.fill();

        }

    }


    /* ======================================================
       ANIMATION LOOP
    ====================================================== */

    function animatePlanet() {

        pctx.clearRect(
            0,
            0,
            SIZE,
            SIZE
        );


        drawOrbitPaths();

        drawDataOrbit();

        drawEarth();

        drawNetwork();

        drawSatellites();


        // rotation += .0015;

        // cloudRotation += .0021;

        // networkRotation += .00015;

        rotation += .00045;        // Earth rotation
cloudRotation += .00065;   // Clouds move slightly faster than Earth
networkRotation += .00005;


        requestAnimationFrame(
            animatePlanet
        );

    }


    animatePlanet();

}

/* ==========================================================
   RAYA ARCHITECTURE INTERACTION
========================================================== */

const architecture =
    document.querySelector(".neural-architecture");

if (architecture) {

    const architectureNodes =
        architecture.querySelectorAll(".neural-node");

    const neuralPaths =
        architecture.querySelectorAll(".neural-path");


    architectureNodes.forEach(node => {

    node.addEventListener("mouseenter", () => {

        const target = node.dataset.node;

        architecture.classList.add("has-active");

        node.classList.add("active");

        if (target === "energy") {

            neuralPaths.forEach(path => {
                path.classList.add("active");
            });

            architectureNodes.forEach(n => {
                n.classList.add("active");
            });

        } else {

            neuralPaths.forEach(path => {

                if (path.dataset.node === target) {

                    path.classList.add("active");

                }

            });

        }

    });


    node.addEventListener("mouseleave", () => {

        architecture.classList.remove("has-active");

        architectureNodes.forEach(n => {

            n.classList.remove("active");

        });

        neuralPaths.forEach(path => {

            path.classList.remove("active");

        });

    });

});

}
/* ==========================================================
   CINEMATIC FINAL EARTH
========================================================== */

const finalCanvas =
    document.getElementById("finalEarthCanvas");


if (finalCanvas) {

    const fctx =
        finalCanvas.getContext("2d");

    const FINAL_SIZE = 620;

    const DPR =
        window.devicePixelRatio || 1;


    finalCanvas.width =
        FINAL_SIZE * DPR;

    finalCanvas.height =
        FINAL_SIZE * DPR;

    fctx.scale(DPR, DPR);


    const fcx =
        FINAL_SIZE / 2;

    const fcy =
        FINAL_SIZE / 2;

    const radius = 195;


    let finalRotation = 0;

    let finalProgress = 0;

    /* ==========================================
   REAL EARTH TEXTURE
========================================== */

// const earthTexture = new Image();

// earthTexture.src = "../assets/earth_day.png";

// let earthTextureReady = false;

// earthTexture.onload = function () {
//     earthTextureReady = true;
// };


/* Offscreen canvas used for spherical Earth */

// const earthBuffer =
//     document.createElement("canvas");

// earthBuffer.width = radius * 2;
// earthBuffer.height = radius * 2;

// const earthBufferCtx =
//     earthBuffer.getContext("2d");


//     /* ==========================================
//        GLOBAL LIGHT LOCATIONS
//     ========================================== */

    const worldLights = [

        {lat:.70, lon:.20},
        {lat:.55, lon:.55},
        {lat:.38, lon:.95},
        {lat:.25, lon:1.35},
        {lat:.05, lon:1.65},

        {lat:-.20, lon:1.95},
        {lat:-.42, lon:2.30},

        {lat:.60, lon:2.80},
        {lat:.30, lon:3.10},
        {lat:.05, lon:3.45},

        {lat:-.35, lon:3.80},

        {lat:.48, lon:4.20},
        {lat:.22, lon:4.55},

        {lat:-.12, lon:4.90},
        {lat:-.45, lon:5.20},

        {lat:.68, lon:5.55},
        {lat:.35, lon:5.90}

    ];


    /* ==========================================
       BACKGROUND SURFACE PARTICLES
    ========================================== */

    // const finalSurface = [];

    // for(let i=0;i<300;i++){

    //     finalSurface.push({

    //         lat:
    //             (Math.random()-.5) *
    //             Math.PI,

    //         lon:
    //             Math.random() *
    //             Math.PI*2,

    //         size:
    //             Math.random()*1.4+.25

    //     });

    // }

    /* ==========================================
   EARTH LAND MASSES
   Stylized geographical clusters
========================================== */

const finalSurface = [];


/* create land-density region */

function createLandRegion(
    centerLat,
    centerLon,
    latSpread,
    lonSpread,
    count
){

    for(let i=0;i<count;i++){

        finalSurface.push({

            lat:
                centerLat +
                (Math.random()-.5) *
                latSpread,

            lon:
                centerLon +
                (Math.random()-.5) *
                lonSpread,

            size:
                Math.random()*2.2 + .7

        });

    }

}


/* ==========================================
   APPROXIMATE CONTINENTS
========================================== */


/* North America */

createLandRegion(
    .62,
    4.85,
    .72,
    .85,
    110
);


/* South America */

createLandRegion(
    -.28,
    5.25,
    .90,
    .42,
    85
);


/* Europe */

createLandRegion(
    .70,
    .20,
    .38,
    .48,
    70
);


/* Africa */

createLandRegion(
    .05,
    .35,
    .90,
    .55,
    120
);


/* Asia */

createLandRegion(
    .60,
    1.10,
    .65,
    1.30,
    150
);


/* India / South Asia */

createLandRegion(
    .32,
    1.25,
    .35,
    .30,
    50
);


/* Southeast Asia */

createLandRegion(
    .08,
    1.65,
    .35,
    .55,
    55
);


/* Australia */

createLandRegion(
    -.55,
    2.15,
    .38,
    .52,
    65
);


    /* ==========================================
       SPHERE PROJECTION
    ========================================== */

    function finalProject(
        lat,
        lon,
        r
    ){

        const longitude =
            lon + finalRotation * Math.PI * 2;

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
                fcx + x*r,

            y:
                fcy - y*r,

            z

        };

    }


    /* ==========================================
       DARK EARTH
    ========================================== */

    function drawFinalEarth(){

        fctx.save();


        fctx.beginPath();

        fctx.arc(
            fcx,
            fcy,
            radius,
            0,
            Math.PI*2
        );

        fctx.clip();


        const ocean =
            fctx.createRadialGradient(

                fcx-65,
                fcy-70,
                15,

                fcx,
                fcy,
                radius

            );


        ocean.addColorStop(
            0,
            "#071828"
        );

        ocean.addColorStop(
            .5,
            "#030c17"
        );

        ocean.addColorStop(
            1,
            "#010307"
        );


        fctx.fillStyle =
            ocean;

        fctx.fillRect(
            fcx-radius,
            fcy-radius,
            radius*2,
            radius*2
        );


        /* faint continental texture */

        // finalSurface.forEach(p=>{

        //     const pos =
        //         finalProject(
        //             p.lat,
        //             p.lon,
        //             radius-3
        //         );


        //     if(pos.z <= 0)
        //         return;


        //     fctx.beginPath();

        //     fctx.arc(
        //         pos.x,
        //         pos.y,
        //         p.size,
        //         0,
        //         Math.PI*2
        //     );


        //     fctx.fillStyle =
        //         `rgba(
        //             55,
        //             85,
        //             90,
        //             ${.04 + pos.z*.09}
        //         )`;


        //     fctx.fill();

        // });

        finalSurface.forEach(p => {

    const pos =
        finalProject(
            p.lat,
            p.lon,
            radius - 3
        );

    if(pos.z <= 0)
        return;


    fctx.beginPath();

    fctx.arc(
        pos.x,
        pos.y,
        p.size * (.65 + pos.z*.45),
        0,
        Math.PI*2
    );


    fctx.fillStyle =
        `rgba(
            35,
            88,
            78,
            ${.10 + pos.z*.16}
        )`;


    fctx.fill();

});


        fctx.restore();


        /* rim */

        fctx.beginPath();

        fctx.arc(
            fcx,
            fcy,
            radius,
            0,
            Math.PI*2
        );


        fctx.strokeStyle =
            "rgba(80,190,220,.20)";

        fctx.lineWidth = 1;

        fctx.stroke();

    }

// function drawFinalEarth() {

//     /* ==========================================
//        REAL ROTATING EARTH
//     ========================================== */

//     if (earthTextureReady) {

//         const diameter = radius * 2;

//         earthBufferCtx.clearRect(
//             0,
//             0,
//             diameter,
//             diameter
//         );


//         /*
//          * Build the globe one vertical strip at a time.
//          *
//          * sin() creates spherical distortion:
//          * center = normal width
//          * edges = geographically compressed
//          */

//         for (let x = -radius; x < radius; x += 2) {

//             const normalizedX =
//                 x / radius;

//             const sphereLongitude =
//                 Math.asin(normalizedX);

//             /*
//              * Convert globe longitude into
//              * horizontal texture position.
//              */

//             let textureX =
//                 (
//                     sphereLongitude /
//                     Math.PI +
//                     0.5 +
//                     finalRotation
//                 ) %
//                 1;

//             if (textureX < 0)
//                 textureX += 1;


//             textureX *=
//                 earthTexture.width;


//             /*
//              * Height of sphere at this X
//              */

//             const sphereHeight =
//                 Math.sqrt(
//                     1 -
//                     normalizedX *
//                     normalizedX
//                 );


//             const columnHeight =
//                 diameter *
//                 sphereHeight;


//             const destinationY =
//                 radius -
//                 columnHeight / 2;


//             /*
//              * Draw a thin strip of
//              * the Earth texture
//              */

//             earthBufferCtx.drawImage(

//                 earthTexture,

//                 textureX,
//                 0,

//                 2,
//                 earthTexture.height,

//                 x + radius,
//                 destinationY,

//                 2,
//                 columnHeight

//             );

//         }


//         /* ==========================================
//            DRAW SPHERE
//         ========================================== */

//         fctx.save();

//         fctx.beginPath();

//         fctx.arc(
//             fcx,
//             fcy,
//             radius,
//             0,
//             Math.PI * 2
//         );

//         fctx.clip();


//         fctx.drawImage(
//             earthBuffer,

//             fcx - radius,
//             fcy - radius,

//             diameter,
//             diameter
//         );


//         /* ==========================================
//            REALISTIC LIGHT / SHADOW
//         ========================================== */

//         const light =
//             fctx.createRadialGradient(

//                 fcx - 75,
//                 fcy - 70,
//                 20,

//                 fcx,
//                 fcy,
//                 radius * 1.2

//             );


//         light.addColorStop(
//             0,
//             "rgba(255,255,255,.12)"
//         );

//         light.addColorStop(
//             .42,
//             "rgba(0,0,0,.05)"
//         );

//         light.addColorStop(
//             .72,
//             "rgba(0,5,15,.32)"
//         );

//         light.addColorStop(
//             1,
//             "rgba(0,2,8,.82)"
//         );


//         fctx.fillStyle = light;

//         fctx.fillRect(
//             fcx - radius,
//             fcy - radius,
//             diameter,
//             diameter
//         );


//         /* ==========================================
//            SLIGHT BLUE ATMOSPHERIC TINT
//         ========================================== */

//         const atmosphere =
//             fctx.createRadialGradient(

//                 fcx,
//                 fcy,
//                 radius * .55,

//                 fcx,
//                 fcy,
//                 radius

//             );


//         atmosphere.addColorStop(
//             0,
//             "rgba(0,0,0,0)"
//         );

//         atmosphere.addColorStop(
//             .78,
//             "rgba(20,90,150,.03)"
//         );

//         atmosphere.addColorStop(
//             1,
//             "rgba(60,180,255,.16)"
//         );


//         fctx.fillStyle =
//             atmosphere;

//         fctx.fillRect(
//             fcx - radius,
//             fcy - radius,
//             diameter,
//             diameter
//         );


//         fctx.restore();

//     }


//     /* ==========================================
//        ATMOSPHERIC RIM
//     ========================================== */

//     fctx.beginPath();

//     fctx.arc(
//         fcx,
//         fcy,
//         radius,
//         0,
//         Math.PI * 2
//     );

//     fctx.strokeStyle =
//         "rgba(90,200,255,.35)";

//     fctx.lineWidth = 1.5;

//     fctx.shadowColor =
//         "rgba(40,170,255,.45)";

//     fctx.shadowBlur = 10;

//     fctx.stroke();

//     fctx.shadowBlur = 0;

// }


    /* ==========================================
       NETWORK
    ========================================== */

    function drawFinalNetwork(){

        const points =
            worldLights.map(light =>
                finalProject(
                    light.lat,
                    light.lon,
                    radius+2
                )
            );


        /* CONNECTIONS */

        if(finalProgress > .38){

            const networkOpacity =
                Math.min(
                    1,
                    (finalProgress-.38)/.32
                );


            points.forEach(
                (point,index)=>{


                    if(point.z <= 0)
                        return;


                    const connections = [

                        points[
                            (index+2) %
                            points.length
                        ],

                        points[
                            (index+5) %
                            points.length
                        ]

                    ];


                    connections.forEach(
                        target=>{


                            if(target.z <= 0)
                                return;


                            fctx.beginPath();

                            fctx.moveTo(
                                point.x,
                                point.y
                            );


                            const mx =
                                (point.x+
                                 target.x)/2;


                            const my =
                                (point.y+
                                 target.y)/2
                                - 18;


                            fctx.quadraticCurveTo(

                                mx,
                                my,

                                target.x,
                                target.y

                            );


                            fctx.strokeStyle =
                                `rgba(
                                    50,
                                    220,
                                    245,
                                    ${
                                    networkOpacity *
                                    .20
                                    }
                                )`;


                            fctx.lineWidth =
                                .7;


                            fctx.stroke();

                        });

                });

        }


        /* LIGHTS */

        const visibleLights =
            Math.floor(
                finalProgress *
                worldLights.length
            );


        points.forEach(
            (point,index)=>{


                if(
                    point.z <= 0 ||
                    index > visibleLights
                )
                    return;


                const glow =
                    .35 +
                    point.z*.65;


                fctx.beginPath();

                fctx.arc(
                    point.x,
                    point.y,
                    2,
                    0,
                    Math.PI*2
                );


                // fctx.fillStyle =
                //     `rgba(
                //         150,
                //         245,
                //         255,
                //         ${glow}
                //     )`;

                /* slightly warm civilization lights */

fctx.fillStyle =
    `rgba(
        255,
        220,
        150,
        ${glow}
    )`;

fctx.shadowColor =
    "rgba(255,205,120,.9)";

fctx.shadowBlur =
    10;


                // fctx.shadowColor =
                //     "#22e8ff";

                // fctx.shadowBlur =
                //     12;


                fctx.fill();


                fctx.shadowBlur =
                    0;

            });

    }


    /* ==========================================
       ANIMATION
    ========================================== */

    function animateFinalEarth(){

        fctx.clearRect(
            0,
            0,
            FINAL_SIZE,
            FINAL_SIZE
        );


        const finalSlide =
            document.getElementById(
                "slide6"
            );


        if(
            finalSlide &&
            finalSlide.classList.contains(
                "active"
            )
        ){

            finalProgress += .0022;

            if(finalProgress > 1)
                finalProgress = 1;

        }


        drawFinalEarth();

        drawFinalNetwork();


        finalRotation += .000035;


        requestAnimationFrame(
            animateFinalEarth
        );

    }


    animateFinalEarth();


    /* used when replaying slide */

    window.resetFinalEarth = function(){

        finalProgress = 0;

    };

}

/* ==========================================================
   REAL-TIME PLANETARY BACKGROUND
========================================================== */

const bgCanvas =
    document.getElementById("planetaryBgCanvas");

const bgCtx =
    bgCanvas.getContext("2d");

let bgWidth;
let bgHeight;
let bgDpr;

let bgStars = [];
let shootingStar = null;


/* ==========================================================
   RESIZE
========================================================== */

function resizePlanetaryBackground() {

    bgDpr =
        Math.min(
            window.devicePixelRatio || 1,
            2
        );

    bgWidth =
        window.innerWidth;

    bgHeight =
        window.innerHeight;


    bgCanvas.width =
        bgWidth * bgDpr;

    bgCanvas.height =
        bgHeight * bgDpr;


    bgCanvas.style.width =
        bgWidth + "px";

    bgCanvas.style.height =
        bgHeight + "px";


    bgCtx.setTransform(
        bgDpr,
        0,
        0,
        bgDpr,
        0,
        0
    );


    createBackgroundStars();

}


window.addEventListener(
    "resize",
    resizePlanetaryBackground
);


/* ==========================================================
   600 STARS
========================================================== */

function createBackgroundStars() {

    bgStars = [];

    const STAR_COUNT = 600;


    for (
        let i = 0;
        i < STAR_COUNT;
        i++
    ) {

        bgStars.push({

            x:
                Math.random() *
                bgWidth,

            y:
                Math.random() *
                bgHeight,

            size:
                Math.random() * 1.15 + .15,

            brightness:
                Math.random() * .55 + .12,

            phase:
                Math.random() *
                Math.PI * 2,

            speed:
                Math.random() * .8 + .25

        });

    }

}


/* ==========================================================
   DRAW STARS
========================================================== */

function drawBackgroundStars(time) {

    bgStars.forEach(star => {

        const twinkle =
            Math.sin(
                time *
                star.speed +
                star.phase
            );


        const opacity =
            Math.max(
                .08,
                star.brightness +
                twinkle * .12
            );


        bgCtx.beginPath();

        bgCtx.arc(
            star.x,
            star.y,
            star.size,
            0,
            Math.PI * 2
        );


        bgCtx.fillStyle =
            `rgba(
                220,
                240,
                255,
                ${opacity}
            )`;


        bgCtx.fill();

    });

}


/* ==========================================================
   SHOOTING STAR
========================================================== */

function updateShootingStar() {

    /*
     * Very low probability.
     * We don't want meteor shower.
     */

    if (!shootingStar) {

        if (Math.random() < .0015) {

            shootingStar = {

                x:
                    Math.random() *
                    bgWidth * .65,

                y:
                    Math.random() *
                    bgHeight * .30,

                vx: 8,

                vy: 3.5,

                life: 1

            };

        }

        return;

    }


    shootingStar.x +=
        shootingStar.vx;

    shootingStar.y +=
        shootingStar.vy;

    shootingStar.life -=
        .018;


    const tailX =
        shootingStar.x - 100;

    const tailY =
        shootingStar.y - 45;


    const gradient =
        bgCtx.createLinearGradient(

            shootingStar.x,
            shootingStar.y,

            tailX,
            tailY

        );


    gradient.addColorStop(
        0,
        `rgba(
            230,
            250,
            255,
            ${shootingStar.life}
        )`
    );


    gradient.addColorStop(
        1,
        "rgba(100,220,255,0)"
    );


    bgCtx.beginPath();

    bgCtx.moveTo(
        shootingStar.x,
        shootingStar.y
    );

    bgCtx.lineTo(
        tailX,
        tailY
    );

    bgCtx.strokeStyle =
        gradient;

    bgCtx.lineWidth =
        1.3;

    bgCtx.stroke();


    if (
        shootingStar.life <= 0 ||
        shootingStar.x > bgWidth
    ) {

        shootingStar = null;

    }

}


/* ==========================================================
   PROCEDURAL EARTH
========================================================== */

let bgEarthRotation = 0;


/*
 * Fixed land particles.
 * They are generated once rather than every frame.
 */

const bgLand = [];


function createLandCluster(
    lat,
    lon,
    latSpread,
    lonSpread,
    count
) {

    for (
        let i = 0;
        i < count;
        i++
    ) {

        bgLand.push({

            lat:
                lat +
                (Math.random() - .5) *
                latSpread,

            lon:
                lon +
                (Math.random() - .5) *
                lonSpread,

            size:
                Math.random() * 2 + .5

        });

    }

}


/* approximate continental regions */

createLandCluster(
    .60, 4.8,
    .70, .85,
    120
); // North America


createLandCluster(
    -.25, 5.2,
    .90, .40,
    90
); // South America


createLandCluster(
    .68, .20,
    .35, .45,
    75
); // Europe


createLandCluster(
    .05, .35,
    .90, .55,
    130
); // Africa


createLandCluster(
    .55, 1.15,
    .65, 1.30,
    180
); // Asia


createLandCluster(
    -.52, 2.1,
    .35, .50,
    70
); // Australia


/* ==========================================================
   EARTH PROJECTION
========================================================== */

function projectBackgroundEarth(
    lat,
    lon,
    radius,
    cx,
    cy
) {

    const longitude =
        lon +
        bgEarthRotation;


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
            cx +
            x * radius,

        y:
            cy -
            y * radius,

        z

    };

}


/* ==========================================================
   DRAW EARTH
========================================================== */

function drawBackgroundEarth() {

    /*
     * Large Earth, mostly outside viewport.
     *
     * This gives us a planetary horizon
     * instead of a distracting full globe.
     */

    const radius =
        Math.min(
            bgWidth * .42,
            650
        );


    const cx =
        bgWidth / 2;


    const cy =
        bgHeight +
        radius * .30;


    bgCtx.save();


    /* circular clipping */

    bgCtx.beginPath();

    bgCtx.arc(
        cx,
        cy,
        radius,
        0,
        Math.PI * 2
    );

    bgCtx.clip();


    /* ==========================================
       OCEAN
    ========================================== */

    const ocean =
        bgCtx.createRadialGradient(

            cx - radius * .30,
            cy - radius * .40,
            radius * .05,

            cx,
            cy,
            radius

        );


    ocean.addColorStop(
        0,
        "#0b456d"
    );

    ocean.addColorStop(
        .42,
        "#062b4b"
    );

    ocean.addColorStop(
        .78,
        "#031426"
    );

    ocean.addColorStop(
        1,
        "#010711"
    );


    bgCtx.fillStyle =
        ocean;


    bgCtx.fillRect(
        cx - radius,
        cy - radius,
        radius * 2,
        radius * 2
    );


    /* ==========================================
       LAND
    ========================================== */

    bgLand.forEach(point => {

        const pos =
            projectBackgroundEarth(

                point.lat,
                point.lon,

                radius - 3,

                cx,
                cy

            );


        if (pos.z <= 0)
            return;


        const opacity =
            .08 +
            pos.z * .16;


        bgCtx.beginPath();


        bgCtx.arc(
            pos.x,
            pos.y,
            point.size *
            (.7 + pos.z * .5),
            0,
            Math.PI * 2
        );


        bgCtx.fillStyle =
            `rgba(
                40,
                115,
                95,
                ${opacity}
            )`;


        bgCtx.fill();

    });


    /* ==========================================
       NIGHT SIDE
    ========================================== */

    const shadow =
        bgCtx.createLinearGradient(

            cx - radius,
            cy,

            cx + radius,
            cy

        );


    shadow.addColorStop(
        0,
        "rgba(0,0,0,.10)"
    );

    shadow.addColorStop(
        .48,
        "rgba(0,0,0,.20)"
    );

    shadow.addColorStop(
        1,
        "rgba(0,0,0,.90)"
    );


    bgCtx.fillStyle =
        shadow;


    bgCtx.fillRect(
        cx - radius,
        cy - radius,
        radius * 2,
        radius * 2
    );


    bgCtx.restore();


    /* ==========================================
       ATMOSPHERIC EDGE
    ========================================== */

    bgCtx.beginPath();

    bgCtx.arc(
        cx,
        cy,
        radius,
        0,
        Math.PI * 2
    );


    bgCtx.strokeStyle =
        "rgba(70,200,255,.32)";

    bgCtx.lineWidth =
        1.2;


    bgCtx.shadowColor =
        "rgba(20,180,255,.30)";

    bgCtx.shadowBlur =
        18;


    bgCtx.stroke();


    bgCtx.shadowBlur = 0;


    /*
     * ~150-second rotation at 60fps.
     */

    bgEarthRotation +=
        (Math.PI * 2) /
        (150 * 60);

}


/* ==========================================================
   MAIN SIMULATION LOOP
========================================================== */

function animatePlanetaryBackground(timestamp) {

    const time =
        timestamp * .001;


    bgCtx.clearRect(
        0,
        0,
        bgWidth,
        bgHeight
    );


    /* Layer 1 */

    drawBackgroundStars(time);

    updateShootingStar();


    /* Layer 3 */

    drawBackgroundEarth();


    requestAnimationFrame(
        animatePlanetaryBackground
    );

}


resizePlanetaryBackground();


requestAnimationFrame(
    animatePlanetaryBackground
);