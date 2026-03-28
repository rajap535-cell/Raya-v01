// subtle reveal (no aggressive animation)

const cards = document.querySelectorAll('.card');

const observer = new IntersectionObserver((entries)=>{
  entries.forEach(entry=>{
    if(entry.isIntersecting){
      entry.target.style.opacity = "1";
      entry.target.style.transform = "translateY(0)";
    }
  });
},{ threshold: 0.2 });

cards.forEach(card=>{
  card.style.opacity = "0";
  card.style.transform = "translateY(20px)";
  card.style.transition = "all 0.6s ease";
  observer.observe(card);
});


// SHOW BUTTONS AFTER SCROLL
const buttons = document.getElementById('entryButtons');

window.addEventListener('scroll', () => {
  const triggerPoint = window.innerHeight * 0.6;

  if(window.scrollY > triggerPoint){
    buttons.classList.add('show');
  }
});