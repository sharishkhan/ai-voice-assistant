import ast
import operator
import random
import re


class LocalFallbackService:
    def __init__(self, assistant_name: str) -> None:
        self.assistant_name = assistant_name
        self.jokes = {
            "default": [
                "Why don't skeletons fight each other? Because they don't have the guts.",
                "What do you call cheese that isn't yours? Nacho cheese.",
                "Why did the scarecrow win an award? Because he was outstanding in his field.",
            ],
            "tech": [
                "Why did the developer go broke? Because he used up all his cache.",
                "Why do programmers prefer dark mode? Because light attracts bugs.",
                "Why was the computer cold? It left its Windows open.",
            ],
            "short": [
                "I used to hate facial hair, but then it grew on me.",
                "Parallel lines have so much in common. It's a shame they'll never meet.",
                "I only know 25 letters of the alphabet. I don't know y.",
            ],
            "kid": [
                "Why did the teddy bear skip dessert? Because it was already stuffed.",
                "What kind of tree fits in your hand? A palm tree.",
                "Why can't your nose be 12 inches long? Because then it would be a foot.",
            ],
        }
        self.simple_facts = {
            "capital of india": "The capital of India is New Delhi.",
            "capital of france": "The capital of France is Paris.",
            "capital of japan": "The capital of Japan is Tokyo.",
            "capital of usa": "The capital of the USA is Washington, D.C.",
            "who made you": f"I was set up here as {self.assistant_name}, a Flask voice assistant with a local fallback mode.",
            "who are you": f"I'm {self.assistant_name}, your voice-powered assistant. Right now I'm answering in local fallback mode.",
        }

    def generate_reply(
        self,
        user_message: str,
        weather_context: str | None = None,
        history: list[dict] | None = None,
    ) -> str:
        lowered = user_message.lower().strip()
        tokens = re.findall(r"\b[a-z']+\b", lowered)
        history = history or []

        joke_follow_up = self._handle_joke_follow_up(lowered, history)
        if joke_follow_up is not None:
            return joke_follow_up

        if any(word in tokens for word in ["hello", "hi", "hey"]):
            return (
                f"Hi, I'm {self.assistant_name}. Gemini is unavailable right now, "
                "but I can still help in local fallback mode."
            )

        if "how are you" in lowered:
            return (
                "I'm doing well. I'm currently running in local fallback mode, "
                "so my answers are simpler than usual."
            )

        if "thank you" in lowered or "thanks" in tokens:
            return "You're welcome. I'm here if you want to try weather, time, or another simple question."

        if any(phrase in lowered for phrase in ["what can you do", "help", "capabilities"]):
            return (
                "Right now I can help with time, date, weather, greetings, calculator math, "
                "jokes, reminder-style prompts, app info, and a few simple knowledge questions "
                "while Gemini is unavailable."
            )

        if weather_context:
            return f"I have live weather data for that request: {weather_context}"

        calculator_result = self._handle_calculation(lowered)
        if calculator_result is not None:
            return calculator_result

        reminder_result = self._handle_reminder(user_message)
        if reminder_result is not None:
            return reminder_result

        joke_result = self._handle_joke(lowered)
        if joke_result is not None:
            return joke_result

        app_info_result = self._handle_app_info(lowered)
        if app_info_result is not None:
            return app_info_result

        fact_result = self._handle_simple_fact(lowered)
        if fact_result is not None:
            return fact_result

        if any(word in lowered for word in ["weather", "temperature", "forecast"]):
            return (
                "I can still handle weather requests through OpenWeather. "
                "Try asking something like weather in Mumbai."
            )

        if any(word in lowered for word in ["time", "date", "day"]):
            return (
                "I can answer time and date questions locally. "
                "Try asking what time is it."
            )

        if lowered.endswith("?"):
            return (
                "I'm in local fallback mode because the Gemini API is unavailable right now. "
                "I may not answer open-ended questions well, but I can still help with weather, "
                "time, date, and a few simple prompts."
            )

        return (
            "I'm in local fallback mode right now because Gemini is unavailable. "
            "Try a weather request, a time question, a simple calculation, a joke, or ask for help."
        )

    def _handle_joke(self, lowered: str) -> str | None:
        if "joke" in lowered or "make me laugh" in lowered:
            return self._pick_joke(lowered)
        return None

    def _handle_joke_follow_up(self, lowered: str, history: list[dict]) -> str | None:
        if not history:
            return None

        recent_assistant_messages = [
            item.get("content", "")
            for item in reversed(history)
            if item.get("role") == "assistant"
        ][:3]
        if not recent_assistant_messages:
            return None

        joke_context_active = any(
            self._looks_like_joke(text) or "another joke" in text.lower()
            for text in recent_assistant_messages
        )
        if not joke_context_active:
            return None

        positive_reaction_phrases = [
            "nice joke",
            "good joke",
            "funny",
            "that was funny",
            "haha",
            "lol",
            "nice one",
        ]
        if any(phrase in lowered for phrase in positive_reaction_phrases):
            return "Thanks. Do you want to hear another joke?"

        another_joke_phrases = [
            "another joke",
            "another one",
            "one more",
            "tell me another",
            "yes",
            "yep",
            "yeah",
            "sure",
            "ok",
            "okay",
        ]
        if lowered in another_joke_phrases or any(
            phrase in lowered for phrase in another_joke_phrases
        ):
            return self._pick_joke(lowered)

        return None

    def _handle_reminder(self, message: str) -> str | None:
        match = re.search(r"remind me to (.+)", message, flags=re.IGNORECASE)
        if not match:
            return None

        reminder_text = match.group(1).strip().rstrip(".")
        if not reminder_text:
            return "Tell me what you'd like to remember, for example: remind me to drink water."
        return (
            f"I can't schedule real reminders in fallback mode, but here's your reminder: {reminder_text}. "
            "You can also copy it into a notes or reminder app."
        )

    def _handle_app_info(self, lowered: str) -> str | None:
        if "how do you work" in lowered or "how does this app work" in lowered:
            return (
                "This app uses Flask on the backend, HTML/CSS/JS on the frontend, "
                "Web Speech API for mic input, SpeechSynthesis for voice output, "
                "OpenWeather for weather, and Gemini when quota is available."
            )
        if "what model" in lowered or "which model" in lowered:
            return "When available, this assistant uses Gemini. Right now you're talking to local fallback mode."
        if "about this app" in lowered or "about this assistant" in lowered:
            return (
                f"{self.assistant_name} is a voice-powered Flask assistant with live weather, "
                "browser speech input/output, and a local fallback mode for basic tasks."
            )
        return None

    def _handle_simple_fact(self, lowered: str) -> str | None:
        normalized = re.sub(r"[?.,!]", "", lowered).strip()
        for prompt, answer in self.simple_facts.items():
            if prompt in normalized:
                return answer
        return None

    def _handle_calculation(self, lowered: str) -> str | None:
        cleaned = lowered.strip()
        trigger_phrases = [
            "calculate ",
            "what is ",
            "what's ",
            "solve ",
        ]
        expression = None
        for phrase in trigger_phrases:
            if cleaned.startswith(phrase):
                expression = cleaned[len(phrase):]
                break

        if expression is None and re.fullmatch(r"[0-9\s+\-*/().%]+", cleaned):
            expression = cleaned

        if expression is None:
            return None

        expression = expression.replace("x", "*")
        expression = expression.replace("plus", "+")
        expression = expression.replace("minus", "-")
        expression = expression.replace("times", "*")
        expression = expression.replace("multiplied by", "*")
        expression = expression.replace("divided by", "/")
        expression = expression.replace("over", "/")
        expression = expression.replace("^", "**")
        expression = expression.strip(" ?")

        if not re.fullmatch(r"[0-9\s+\-*/().%*]+", expression):
            return None

        try:
            result = self._safe_eval(expression)
        except Exception:
            return "I couldn't solve that safely in fallback mode. Try a simple expression like 12 * 8."

        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return f"The answer is {result}."

    def _safe_eval(self, expression: str) -> float:
        allowed_binary = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
        }
        allowed_unary = {
            ast.UAdd: operator.pos,
            ast.USub: operator.neg,
        }

        def evaluate(node):
            if isinstance(node, ast.Expression):
                return evaluate(node.body)
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                return node.value
            if isinstance(node, ast.BinOp) and type(node.op) in allowed_binary:
                return allowed_binary[type(node.op)](evaluate(node.left), evaluate(node.right))
            if isinstance(node, ast.UnaryOp) and type(node.op) in allowed_unary:
                return allowed_unary[type(node.op)](evaluate(node.operand))
            raise ValueError("Unsupported expression")

        parsed = ast.parse(expression, mode="eval")
        return evaluate(parsed)

    def _pick_joke(self, lowered: str) -> str:
        category = "default"
        if "tech" in lowered or "programming" in lowered or "developer" in lowered:
            category = "tech"
        elif "short" in lowered:
            category = "short"
        elif "kid" in lowered or "kids" in lowered or "child" in lowered:
            category = "kid"

        return random.choice(self.jokes[category])

    def _looks_like_joke(self, text: str) -> bool:
        lowered = text.lower()
        joke_markers = [
            "why ",
            "what do you call",
            "what kind of",
            "i used to",
            "parallel lines",
            "i only know 25 letters",
        ]
        return any(marker in lowered for marker in joke_markers)
