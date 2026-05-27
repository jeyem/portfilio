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

async function getUserHash() {
  let hash = localStorage.getItem("chat_user_hash");

  if (hash) return hash;

  const raw = [
    navigator.userAgent,
    navigator.language,
    screen.width,
    screen.height,
    Intl.DateTimeFormat().resolvedOptions().timeZone
  ].join("|");

  const encoder = new TextEncoder();
  const data = encoder.encode(raw);

  const digest = await crypto.subtle.digest("SHA-256", data);

  hash = Array.from(new Uint8Array(digest))
    .map(b => b.toString(16).padStart(2, "0"))
    .join("");

  localStorage.setItem("chat_user_hash", hash);

  return hash;
}

async function sendMessageToBot(message) {
  const res = await fetch("https://chat.e-mahmoudi.me/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      message,
      user_hash: await getUserHash(),
    })
  });

  const data = await res.json();
  return data.message.content;
}

function showTypingIndicator() {
  const div = document.createElement("div");
  div.className = "bot-message";

  div.innerHTML = `
    <div class="typing">
      <span></span>
      <span></span>
      <span></span>
    </div>
  `;

  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  return div;
}

// === CHAT WIDGET LOGIC ===
const chatToggle = document.getElementById("chat-toggle");
const chatDialog = document.getElementById("chat-dialog");
const chatMessages = document.getElementById("chat-messages");
const chatInput = document.getElementById("chat-input");
const chatSendBtn = document.getElementById("chat-send");
const chatCloseBtn = document.getElementById("chat-close");

// Append message
function appendMessage(sender, text) {
  const messageDiv = document.createElement("div");

  messageDiv.className =
    sender === "user" ? "user-message" : "bot-message";

  messageDiv.textContent = text;

  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

setTimeout(() => chatDialog.classList.remove("hidden"), 10000);

// Open chat
chatToggle.addEventListener("click", () => {
  chatDialog.classList.remove("hidden");
});

// Close chat
chatCloseBtn.addEventListener("click", () => {
  chatDialog.classList.add("hidden");
});

// Send message
async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) return;

  appendMessage("user", text);
  chatInput.value = "";

  // disable input while waiting
  chatInput.disabled = true;
  chatSendBtn.disabled = true;
  chatInput.placeholder = "Ehsan is thinking...";

  const typingBubble = showTypingIndicator();

  try {
    const reply = await sendMessageToBot(text);

    typingBubble.textContent = reply;

  } catch (err) {
    typingBubble.textContent =
      "Sorry, something went wrong. Please try again.";
    console.error(err);

  } finally {
    chatInput.disabled = false;
    chatSendBtn.disabled = false;
    chatInput.placeholder = "Ask something...";
    chatInput.focus();
  }
}

// Send button
chatSendBtn.addEventListener("click", sendMessage);

// Enter key
chatInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    sendMessage();
  }
});

// Hide on page load
document.addEventListener("DOMContentLoaded", () => {
  chatDialog.classList.add("hidden");
});
