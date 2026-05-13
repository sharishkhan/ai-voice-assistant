from google import genai
from google.genai.errors import ClientError
from google.genai import types


class AIService:
    def __init__(self, api_key: str, model_name: str, assistant_name: str) -> None:
        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=30_000,
                client_args={"trust_env": False},
            ),
        )
        self.model_name = model_name
        self.assistant_name = assistant_name

    def generate_reply(
        self,
        user_message: str,
        history: str,
        weather_context: str | None = None,
    ) -> dict:
        instructions = [
            f"You are {self.assistant_name}, a friendly AI voice assistant.",
            "Reply naturally so your answer sounds good when read aloud.",
            "Keep answers concise unless the user asks for detail.",
            "Use plain text only.",
        ]

        if weather_context:
            instructions.append(f"Use this live weather data when relevant: {weather_context}")

        prompt = "\n".join(
            [
                *instructions,
                "",
                "Recent conversation:",
                history or "No previous conversation.",
                "",
                f"User: {user_message}",
                "Assistant:",
            ]
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            return {
                "reply": (response.text or "").strip() or "I couldn't generate a response right now.",
                "source": "gemini",
            }
        except ClientError as error:
            message = str(error)
            if "429" in message or "RESOURCE_EXHAUSTED" in message:
                return {
                    "reply": (
                        "Your Gemini API free-tier quota for this model is exhausted right now."
                    ),
                    "source": "gemini-error",
                    "error_type": "quota_exhausted",
                }
            return {
                "reply": "Gemini returned an API error.",
                "source": "gemini-error",
                "error_type": "api_error",
            }
        except Exception:
            return {
                "reply": "I couldn't reach the Gemini API right now.",
                "source": "gemini-error",
                "error_type": "network_error",
            }
