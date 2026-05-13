const chatLog = document.getElementById("chat-log");
const input = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const micButton = document.getElementById("mic-button");
const weatherButton = document.getElementById("weather-button");
const voiceToggle = document.getElementById("voice-toggle");
const statusLine = document.getElementById("status");
const assistantName = document.getElementById("assistant-name")?.textContent || "Astra";
const toastStack = document.getElementById("toast-stack");

const appState = {
  history: [],
};

function showToast(message, type = "info") {
  if (!toastStack) return;
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  toastStack.appendChild(toast);

  window.setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(-4px)";
  }, 2800);

  window.setTimeout(() => {
    toast.remove();
  }, 3200);
}

function addMessage(role, content, options = {}) {
  const message = document.createElement("div");
  message.className = `message ${role}`;
  message.textContent = content;
  chatLog.appendChild(message);
  chatLog.scrollTop = chatLog.scrollHeight;
  if (options.persist !== false) {
    appState.history.push({ role, content });
  }
}

function addTypingBubble() {
  const bubble = document.createElement("div");
  bubble.className = "message assistant";
  bubble.id = "typing-bubble";
  bubble.innerHTML = `
    <div class="typing-indicator" aria-label="Assistant is typing">
      <span></span><span></span><span></span>
    </div>
  `;
  chatLog.appendChild(bubble);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function removeTypingBubble() {
  document.getElementById("typing-bubble")?.remove();
}

function typeAssistantMessage(text) {
  const message = document.createElement("div");
  message.className = "message assistant";
  chatLog.appendChild(message);

  let index = 0;
  return new Promise((resolve) => {
    const timer = setInterval(() => {
      message.textContent = text.slice(0, index);
      index += 1;
      chatLog.scrollTop = chatLog.scrollHeight;

      if (index > text.length) {
        clearInterval(timer);
        appState.history.push({ role: "assistant", content: text });
        window.speechModule.speak(text);
        resolve();
      }
    }, 18);
  });
}

async function sendMessage(prefilledMessage = null) {
  const text = (prefilledMessage ?? input.value).trim();
  if (!text) return;

  addMessage("user", text);
  const historyForRequest = appState.history.slice(0, -1);
  input.value = "";
  statusLine.textContent = `${assistantName} is thinking...`;
  addTypingBubble();

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        history: historyForRequest,
      }),
    });
    const raw = await response.text();
    let data = {};
    try {
      data = raw ? JSON.parse(raw) : {};
    } catch (error) {
      data = { error: "The server returned an unexpected response." };
    }
    removeTypingBubble();

    if (!response.ok) {
      showToast(data.error || "Something went wrong.", "error");
      statusLine.textContent = "Request failed.";
      return;
    }

    if (data.weather) {
      window.weatherModule.renderWeatherCard(data.weather);
    }

    if (data.source === "local-fallback") {
      const reasonMap = {
        quota_exhausted: "Gemini quota is exhausted, so local fallback mode is active.",
        api_error: "Gemini returned an API error, so local fallback mode is active.",
        network_error: "Gemini is unreachable, so local fallback mode is active.",
      };
      showToast(reasonMap[data.fallback_reason] || "Local fallback mode is active.", "info");
    }

    await typeAssistantMessage(data.reply);
    statusLine.textContent = "Ready for the next message.";
  } catch (error) {
    removeTypingBubble();
    showToast("I hit a network error. Please try again.", "error");
    statusLine.textContent = "Network error.";
  }
}

async function fetchWeatherPrompt() {
  const city = window.prompt("Enter a city for live weather:");
  if (!city) return;

  statusLine.textContent = `Fetching weather for ${city}...`;
  try {
    const result = await window.weatherModule.fetchWeather(city);
    window.weatherModule.renderWeatherCard(result.data);

    if (!result.ok) {
      showToast(result.data.error || "Could not load weather.", "error");
      statusLine.textContent = "Could not load weather.";
      return;
    }

    addMessage("user", `Weather in ${city}`);
    await typeAssistantMessage(
      `Right now in ${result.data.city}, it's ${Math.round(result.data.temperature)}C with ${result.data.description.toLowerCase()}. It feels like ${Math.round(result.data.feels_like)}C.`
    );
    statusLine.textContent = "Weather updated.";
    showToast(`Weather updated for ${result.data.city}.`, "success");
  } catch (error) {
    showToast("Weather request failed.", "error");
    statusLine.textContent = "Weather request failed.";
  }
}

async function loadHistory() {
  try {
    const response = await fetch("/api/history?limit=24");
    if (!response.ok) return false;
    const data = await response.json();
    const messages = Array.isArray(data.messages) ? data.messages : [];
    if (!messages.length) return false;

    chatLog.innerHTML = "";
    appState.history = [];
    for (const item of messages) {
      addMessage(item.role, item.content);
    }
    statusLine.textContent = "Previous conversation restored.";
    showToast("Restored recent chat history.", "info");
    return true;
  } catch (error) {
    showToast("Could not restore chat history.", "error");
    return false;
  }
}

sendButton.addEventListener("click", () => sendMessage());
input.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    sendMessage();
  }
});
weatherButton.addEventListener("click", fetchWeatherPrompt);
micButton.addEventListener("click", () => window.speechModule.startListening());
voiceToggle.addEventListener("click", () => {
  const enabled = window.speechModule.toggleVoice();
  voiceToggle.textContent = enabled ? "Voice On" : "Voice Off";
  statusLine.textContent = enabled ? "Speech output enabled." : "Speech output disabled.";
});

window.speechModule.loadConfig();
window.speechModule.setupRecognition({
  micButton,
  statusLine,
  onTranscript: (transcript) => {
    if (!transcript) {
      statusLine.textContent = "I didn't catch that. Please try again.";
      showToast("I didn't catch that. Please try again.", "error");
      return;
    }
    input.value = transcript;
    statusLine.textContent = `Voice captured: "${transcript}"`;
    showToast(`Voice captured: "${transcript}"`, "info");
    sendMessage(transcript);
  },
});

(async () => {
  const restored = await loadHistory();
  if (!restored) {
    addMessage(
      "assistant",
      `Hi, I'm ${assistantName}. Ask me anything, or try saying weather in Delhi.`
    );
  }
})();
