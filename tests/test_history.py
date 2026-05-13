from utils.helpers import init_chat_db, load_chat_history, save_chat_message


def test_chat_history_round_trip(tmp_path):
    db_path = tmp_path / "chat_history.db"

    init_chat_db(str(db_path))
    save_chat_message(str(db_path), "user", "Hello")
    save_chat_message(str(db_path), "assistant", "Hi there")

    history = load_chat_history(str(db_path), limit=5)

    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"
    assert history[1]["role"] == "assistant"
