// ---- Nav scroll effect ----
const nav = document.getElementById('mainNav');
window.addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', window.scrollY > 60);
});

// ---- Hamburger menu ----
const hamburger = document.getElementById('navHamburger');
if (hamburger) {
  hamburger.addEventListener('click', () => {
    nav.classList.toggle('menu-open');
  });
  document.getElementById('navLinks').querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => nav.classList.remove('menu-open'));
  });
  document.addEventListener('click', e => {
    if (!nav.contains(e.target)) nav.classList.remove('menu-open');
  });
}

// ---- Story accordion ----
document.querySelectorAll('.story-item').forEach(item => {
  item.querySelector('.story-header').addEventListener('click', () => {
    const wasActive = item.classList.contains('active');
    document.querySelectorAll('.story-item').forEach(s => s.classList.remove('active'));
    if (!wasActive) item.classList.add('active');
  });
});

// ---- Chain tabs ----
const addresses = {
  ethereum: '0x0eF141188cc4E8E0f8022ad7c50172f0feEE9Ca8',
  bitcoin: 'bc1pc8vuu2va29wp3mlf5zye7pfl0g350agxeerqe67hm3jt6876cleqhxutmd',
  bsc: '0x0eF141188cc4E8E0f8022ad7c50172f0feEE9Ca8',
  xrp: 'rKSCtxX1EMpLd2TK1y9sreNb3QAKnT12DG',
  cardano: 'addr1qxgp4e62vnqpp4u3nxmlsy6f484h4gfhup2sdznm3c2tena9dve7tnrgrjhkvepdapa7eus0a9y57aty6tla62yj0rnqpy7wcq'
};
let currentChain = 'ethereum';

document.querySelectorAll('.chain-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.chain-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    currentChain = tab.dataset.chain;
    document.getElementById('donateLabel').textContent = currentChain.toUpperCase() + ' ADDRESS';
    document.getElementById('donateAddress').textContent = addresses[currentChain];
    document.getElementById('copyBtn').textContent = 'Copy Address';
  });
});

// ---- Copy address ----
function copyAddress() {
  navigator.clipboard.writeText(addresses[currentChain]).then(() => {
    const btn = document.getElementById('copyBtn');
    btn.textContent = '✓ Copied!';
    btn.style.background = '#4a9e5b';
    setTimeout(() => {
      btn.textContent = 'Copy Address';
      btn.style.background = '';
    }, 2000);
  });
}

// ---- Scroll reveal ----
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
    }
  });
}, { threshold: 0.15 });

document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

// ---- Lightbox ----
const lightbox = document.getElementById('lightbox');
const lightboxImg = document.getElementById('lightboxImg');

document.querySelectorAll('.story-gallery-item img').forEach(img => {
  img.addEventListener('click', e => {
    e.stopPropagation();
    const fullSrc = img.src.replace('/web/', '/full/');
    lightboxImg.src = fullSrc;
    lightbox.classList.add('active');
  });
});

lightbox.addEventListener('click', () => {
  lightbox.classList.remove('active');
  lightboxImg.src = '';
});

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    lightbox.classList.remove('active');
    lightboxImg.src = '';
  }
});

// ---- Smooth scroll for nav links ----
document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    const target = document.querySelector(link.getAttribute('href'));
    if (target) target.scrollIntoView({ behavior: 'smooth' });
  });
});
