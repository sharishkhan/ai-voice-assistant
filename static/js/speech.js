window.speechModule = (() => {
  let recognition = null;
  let voiceEnabled = true;
  let ttsSettings = {
    lang: "en-US",
    rate: 1,
    pitch: 1,
  };

  async function loadConfig() {
    try {
      const response = await fetch("/api/config");
      if (!response.ok) return;
      const data = await response.json();
      if (data.tts) {
        ttsSettings = { ...ttsSettings, ...data.tts };
      }
    } catch (error) {
      console.error("Could not load frontend config", error);
    }
  }

  function speak(text) {
    if (!voiceEnabled || !("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = ttsSettings.lang;
    utterance.rate = ttsSettings.rate;
    utterance.pitch = ttsSettings.pitch;
    window.speechSynthesis.speak(utterance);
  }

  function setupRecognition({ micButton, statusLine, onTranscript }) {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      micButton.disabled = true;
      micButton.textContent = "Mic NA";
      statusLine.textContent = "Speech recognition is not supported in this browser.";
      return;
    }

    recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.continuous = false;

    recognition.onstart = () => {
      micButton.classList.add("recording");
      statusLine.textContent = "Listening...";
    };

    recognition.onresult = (event) => {
      const transcript = (event.results[0][0].transcript || "").trim();
      onTranscript(transcript);
    };

    recognition.onerror = () => {
      statusLine.textContent = "Mic input failed. Please try again.";
    };

    recognition.onend = () => {
      micButton.classList.remove("recording");
    };
  }

  function startListening() {
    recognition?.start();
  }

  function toggleVoice() {
    voiceEnabled = !voiceEnabled;
    if (!voiceEnabled && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    return voiceEnabled;
  }

  return {
    loadConfig,
    setupRecognition,
    startListening,
    toggleVoice,
    speak,
  };
})();
