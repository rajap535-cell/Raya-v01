// ================= PANEL SYSTEM =================
const panel = document.getElementById('panel');
const layers = document.querySelectorAll('.layer');
const cards = document.querySelectorAll('.card');

const data = {
  data:{title:"Data Foundation",modules:[["Data Ingestion","ACTIVE"],["Normalization Engine","ACTIVE"],["Integrity Check","BUILD"]]},
  intelligence:{title:"Intelligence Layer",modules:[["Advisory Engine","ACTIVE"],["Pattern Recognition","BUILD"]]},
  diagnostics:{title:"Diagnostics Layer",modules:[["Disease Detection","ACTIVE"],["Failure Prediction","BUILD"]]},
  decision:{title:"Decision Layer",modules:[["Optimization Engine","BUILD"],["Simulation","FUTURE"]]},
  autonomy:{title:"Autonomy Layer",modules:[["Self-Healing","FUTURE"],["Adaptive Control","FUTURE"]]}
};

function statusClass(s){
  return s==='ACTIVE'?'active-status':s==='BUILD'?'build-status':'future-status'
}

// ================= LAYER CLICK =================
layers.forEach(layer=>{
  layer.onclick=()=>{
    layers.forEach(l=>l.classList.remove('active'));
    layer.classList.add('active');

    const d=data[layer.dataset.layer];
    let html=`<h3>${d.title}</h3>`;

    d.modules.forEach(m=>{
      html+=`<div class='module'>${m[0]} 
      <span class='status ${statusClass(m[1])}'>${m[1]}</span></div>`;
    });

    panel.innerHTML=html;
  }
});

// default
layers[0].click();

// ================= PARALLAX =================
window.addEventListener('scroll', () => {
  const scrollY = window.scrollY;
  const hero = document.getElementById('heroContent');

  hero.style.transform = `translateY(${scrollY * 0.15}px)`;
});

// ================= CARD EMERGENCE =================
const observer = new IntersectionObserver((entries)=>{
  entries.forEach(entry=>{
    if(entry.isIntersecting){
      entry.target.classList.add('visible');
    }
  });
},{ threshold: 0.2 });

cards.forEach(card=>{
  observer.observe(card);
});

// ================= LAYER BOOT =================
window.addEventListener('load', ()=>{
  layers.forEach((layer, index)=>{
    setTimeout(()=>{
      layer.classList.add('booted');
    }, index * 150);
  });
});

 