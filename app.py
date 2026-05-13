from pathlib import Path

from flask import Flask, jsonify, render_template, request

from services.ai_service import AIService
from services.local_fallback_service import LocalFallbackService
from services.tts_service import TTSService
from services.weather_service import WeatherService
from utils.config import Config
from utils.helpers import (
    build_time_response,
    extract_city_from_message,
    format_chat_history_for_model,
    init_chat_db,
    is_time_query,
    load_chat_history,
    save_chat_message,
)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    init_chat_db(app.config["CHAT_DB_PATH"])

    @app.get("/")
    def index():
        asset_version = int(Path(__file__).stat().st_mtime)
        return render_template(
            "index.html",
            assistant_name=app.config["ASSISTANT_NAME"],
            asset_version=asset_version,
        )

    @app.get("/api/config")
    def frontend_config():
        return jsonify(
            {
                "assistantName": app.config["ASSISTANT_NAME"],
                "tts": TTSService().get_settings(),
            }
        )

    @app.get("/api/weather")
    def weather():
        city = (request.args.get("city") or "").strip()
        if not city:
            return jsonify({"error": "City is required."}), 400

        service = WeatherService(app.config["OPENWEATHER_API_KEY"])
        data = service.get_weather_by_city(city)
        return jsonify(data), 400 if "error" in data else 200

    @app.get("/api/history")
    def history():
        limit = request.args.get("limit", default=20, type=int)
        return jsonify({"messages": load_chat_history(app.config["CHAT_DB_PATH"], limit)})

    @app.post("/api/chat")
    def chat():
        payload = request.get_json(silent=True) or {}
        message = (payload.get("message") or "").strip()
        history = payload.get("history") or []

        if not message:
            return jsonify({"error": "Message is required."}), 400

        if is_time_query(message):
            reply = build_time_response(app.config["APP_TIMEZONE"])
            save_chat_message(app.config["CHAT_DB_PATH"], "user", message)
            save_chat_message(app.config["CHAT_DB_PATH"], "assistant", reply)
            return jsonify({"reply": reply, "source": "local-time"})

        city = extract_city_from_message(message)
        weather_data = None
        weather_context = None

        if city:
            weather_service = WeatherService(app.config["OPENWEATHER_API_KEY"])
            weather_data = weather_service.get_weather_by_city(city)
            if "error" not in weather_data:
                weather_context = weather_service.format_weather_context(weather_data)

        ai_service = AIService(
            api_key=app.config["GEMINI_API_KEY"],
            model_name=app.config["GEMINI_MODEL"],
            assistant_name=app.config["ASSISTANT_NAME"],
        )
        fallback_service = LocalFallbackService(app.config["ASSISTANT_NAME"])
        ai_result = ai_service.generate_reply(
            user_message=message,
            history=format_chat_history_for_model(history),
            weather_context=weather_context,
        )

        reply = ai_result["reply"]
        source = ai_result.get("source", "gemini")
        fallback_reason = None

        if source == "gemini-error":
            fallback_reason = ai_result.get("error_type", "unavailable")
            reply = fallback_service.generate_reply(
                user_message=message,
                weather_context=weather_context,
                history=history,
            )
            source = "local-fallback"

        save_chat_message(app.config["CHAT_DB_PATH"], "user", message)
        save_chat_message(app.config["CHAT_DB_PATH"], "assistant", reply)

        response = {"reply": reply, "source": source}
        if fallback_reason:
            response["fallback_reason"] = fallback_reason
        if weather_data and "error" not in weather_data:
            response["weather"] = weather_data
        return jsonify(response)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
