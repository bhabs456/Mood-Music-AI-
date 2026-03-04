const chatArea = document.getElementById("chatArea");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const themeBtn = document.getElementById("themeBtn");
const nowPlayingEl = document.querySelector(".np-text");
const moodChips = document.querySelectorAll(".mood-chip");

// ── THEME ──────────────────────────────────────
if (localStorage.getItem("moodMusicTheme") === "dark") {
  document.body.classList.add("dark-mode");
}
themeBtn.addEventListener("click", () => {
  // Ripple animation
  themeBtn.classList.remove("clicked");
  void themeBtn.offsetWidth; // reflow
  themeBtn.classList.add("clicked");
  setTimeout(() => themeBtn.classList.remove("clicked"), 500);

  document.body.classList.toggle("dark-mode");
  localStorage.setItem(
    "moodMusicTheme",
    document.body.classList.contains("dark-mode") ? "dark" : "light",
  );
});

// ── MOOD DATA ──────────────────────────────────

const fallbackReplies = [
  "I'd love to help! Could you describe your mood a little more? Try words like <em>happy</em>, <em>sad</em>, <em>romantic</em>, <em>energetic</em>, or <em>focused</em>. 🎶",
  "Hmm, I'm still learning to read moods! Tell me if you feel happy, sad, energetic, romantic, or need to focus — I'll find the perfect playlist. 🎵",
  "Tell me more about how you're feeling! Words like 'joyful', 'melancholy', 'pumped', or 'calm' help me tune into the right music for you. 🎧",
];

// ── HELPERS ────────────────────────────────────
const getTime = () =>
  new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

const randomFallback = () =>
  fallbackReplies[Math.floor(Math.random() * fallbackReplies.length)];

const scrollToBottom = () => {
  chatArea.scrollTop = chatArea.scrollHeight;
};

function appendMessage(content, sender = "bot", htmlContent = "") {
  const row = document.createElement("div");
  row.className = sender === "user" ? "message-row user-row" : "message-row";

  const bubbleInner = htmlContent || `<p>${content}</p>`;

  if (sender === "bot") {
    row.innerHTML = `
      <div class="avatar bot-avatar">🎵</div>
      <div class="msg-group">
        <div class="bubble bot-bubble">${bubbleInner}</div>
        <span class="timestamp">${getTime()}</span>
      </div>
    `;
  } else {
    row.innerHTML = `
      <div class="msg-group user-group">
        <div class="bubble user-bubble">${bubbleInner}</div>
        <span class="timestamp">${getTime()}</span>
      </div>
      <div class="avatar user-avatar">🎧</div>
    `;
  }

  chatArea.appendChild(row);
  scrollToBottom();
}

function showTyping() {
  const row = document.createElement("div");
  row.className = "message-row bot";
  row.id = "typingRow";
  row.innerHTML = `
        <div class="avatar bot-avatar">🎵</div>
        <div class="bubble typing-bubble">
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
        </div>`;
  chatArea.appendChild(row);
  scrollToBottom();
}

const removeTyping = () => {
  const t = document.getElementById("typingRow");
  if (t) t.remove();
};

// ── BOT RESPONSE ───────────────────────────────

// ── SEND MESSAGE ───────────────────────────────
function sendMessage() {
  const input = document.getElementById("userInput");
  const chatArea = document.getElementById("chatArea");

  const userMessage = input.value.trim();
  if (!userMessage) return;

  const time = new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  chatArea.innerHTML += `
  <div class="message-row user-row">
      <div class="msg-group user-group">
          <div class="bubble user-bubble">
              ${userMessage}
          </div>
          <div class="timestamp">${time}</div>
      </div>
      <div class="avatar user-avatar">🙂</div>
  </div>
  `;

  input.value = "";

  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: userMessage }),
  })
    .then((res) => res.json())
    .then((data) => {
      displaySongs(data);
    });
}

function displaySongs(data) {
  const chatArea = document.getElementById("chatArea");
  const time = new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  let songsHTML = `
  <div class="message-row bot">
      <div class="avatar bot-avatar">🎧</div>
      <div class="msg-group">
          <div class="bubble bot-bubble">
              Here are some <b>${data.mood}</b> songs for you
              <ul class="song-list">
  `;

  data.songs.forEach((song, i) => {
    songsHTML += `
      <li class="song-item">
          <a class="song-link" href="${song.link}" target="_blank">
              <span class="song-num">${i + 1}</span>
              <div class="song-info">
                  <div class="song-title">${song.title}</div>
                  <div class="song-artist">${song.artist}</div>
              </div>
          </a>
      </li>
      `;
  });

  songsHTML += `
              </ul>
          </div>
          <div class="timestamp">${time}</div>
      </div>
  </div>
  `;

  chatArea.innerHTML += songsHTML;
  chatArea.scrollTop = chatArea.scrollHeight;
}

// ── EVENTS ────────────────────────────────────
sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});
moodChips.forEach((chip) => {
  chip.addEventListener("click", () => {
    userInput.value = chip.getAttribute("data-mood");
    sendMessage();
  });
});

// ── WELCOME ───────────────────────────────────
window.addEventListener("DOMContentLoaded", () => {
  setTimeout(() => {
    appendMessage(
      "",
      "bot",
      `
          <p>Hi there! 👋 I'm <strong>Mood Music AI</strong>.</p>
          <p style="margin-top:6px;">Tell me how you're feeling and I'll handpick the perfect songs for your mood. 🎵</p>
          <p style="margin-top:6px;font-size:0.8rem;opacity:0.75;">Type freely or tap a mood chip below to get started!</p>`,
    );
    nowPlayingEl.textContent = "🎵 Waiting for your mood…";
  }, 300);
});
