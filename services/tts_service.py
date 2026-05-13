class TTSService:
    def get_settings(self) -> dict:
        return {
            "enabled": True,
            "engine": "SpeechSynthesis",
            "lang": "en-US",
            "rate": 1.0,
            "pitch": 1.0,
        }
