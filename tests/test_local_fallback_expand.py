from services.local_fallback_service import LocalFallbackService


def test_local_fallback_can_calculate():
    service = LocalFallbackService("Astra")

    reply = service.generate_reply("calculate 12 * 8")

    assert "96" in reply


def test_local_fallback_can_handle_reminder_prompt():
    service = LocalFallbackService("Astra")

    reply = service.generate_reply("remind me to drink water")

    assert "drink water" in reply
    assert "reminder" in reply.lower()
