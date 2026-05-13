from services.local_fallback_service import LocalFallbackService


def test_local_fallback_handles_positive_joke_reaction():
    service = LocalFallbackService("Astra")
    history = [
        {
            "role": "assistant",
            "content": "Why did the scarecrow win an award? Because he was outstanding in his field.",
        }
    ]

    reply = service.generate_reply("nice joke", history=history)

    assert "another joke" in reply.lower()


def test_local_fallback_handles_another_joke_follow_up():
    service = LocalFallbackService("Astra")
    history = [
        {
            "role": "assistant",
            "content": "Why did the scarecrow win an award? Because he was outstanding in his field.",
        }
    ]

    reply = service.generate_reply("yes", history=history)

    assert reply
    assert "another joke" not in reply.lower()
