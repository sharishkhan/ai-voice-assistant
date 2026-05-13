from utils.helpers import format_chat_history_for_model


def test_format_chat_history_for_model_formats_entries():
    history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"},
    ]

    result = format_chat_history_for_model(history)

    assert "User: Hello" in result
    assert "Assistant: Hi there" in result
