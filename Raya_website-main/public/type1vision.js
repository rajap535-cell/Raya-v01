/* ==========================================
   RAYA TYPE-1 VISION
========================================== */

const slides = document.getElementById("slides");
const slideList = document.querySelectorAll(".slide");

const dots = document.querySelectorAll(".dot");

const nextBtn = document.getElementById("nextSlide");
const prevBtn = document.getElementById("prevSlide");

const continueBtn = document.querySelector(".continue");

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

    slides.style.transform=
    `translateX(-${current*100}vw)`;

    slideList.forEach(slide=>{

        slide.classList.remove("active");

    });

    slideList[current].classList.add("active");

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

window.addEventListener("wheel",e=>{

    e.preventDefault();

    if(locked)return;

    if(e.deltaY>0){

        nextSlide();

    }else{

        previousSlide();

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