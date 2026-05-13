# AI Voice Assistant

This project is a voice-powered AI assistant built with Flask, HTML, CSS, and JavaScript.

## Features

- Gemini API integration for AI chat
- OpenWeather API integration for live weather
- Web Speech API for microphone input
- SpeechSynthesis for browser voice output
- Typing animation for assistant replies
- SQLite chat history storage
- Modular folder structure

## Folder guide

- `app.py`: Flask entry point and route definitions
- `services/ai_service.py`: Gemini API integration
- `services/weather_service.py`: OpenWeather requests and formatting
- `services/tts_service.py`: Frontend TTS settings provider
- `utils/config.py`: `.env` config loader
- `utils/helpers.py`: shared helpers, city extraction, and SQLite history helpers
- `templates/index.html`: main UI
- `static/css/style.css`: modern styling
- `static/js/main.js`: chat flow and typing animation
- `static/js/speech.js`: mic input and voice output logic
- `static/js/weather.js`: weather fetch and card rendering
- `data/chat_history.db`: local SQLite database for chat history
- `tests/`: starter test suite

## Setup

1. Create a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Add your real keys to `.env`.
4. Run:

```bash
python app.py
```

## Deploying to Render

1. Push the project to GitHub.
2. Create a new Render Web Service.
3. Set build command to `pip install -r requirements.txt`.
4. Set start command to `gunicorn app:app`.
5. Add the same environment variables from `.env` into Render's dashboard.
