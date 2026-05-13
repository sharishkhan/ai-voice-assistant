from services.local_fallback_service import LocalFallbackService


def test_local_fallback_handles_greeting():
    service = LocalFallbackService("Astra")

    reply = service.generate_reply("hello")

    assert "Astra" in reply
    assert "fallback" in reply.lower()
