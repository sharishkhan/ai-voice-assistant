import re
import sqlite3
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def extract_city_from_message(message: str) -> str | None:
    patterns = [
        r"weather in ([a-zA-Z\s\-]+)",
        r"temperature in ([a-zA-Z\s\-]+)",
        r"forecast for ([a-zA-Z\s\-]+)",
    ]

    lowered = message.lower()
    for pattern in patterns:
        match = re.search(pattern, lowered)
        if match:
            return match.group(1).strip().title()
    return None


def format_chat_history_for_model(history: list[dict]) -> str:
    lines = []
    for item in history[-8:]:
        role = item.get("role", "user").title()
        content = (item.get("content") or "").strip()
        if content:
            lines.append(f"{role}: {content}")
    return "\n".join(lines)


def is_time_query(message: str) -> bool:
    lowered = message.lower().strip()
    patterns = [
        "what time is it",
        "tell me the time",
        "current time",
        "time now",
        "what is the time",
        "date today",
        "what date is it",
        "today's date",
        "todays date",
        "what day is it",
    ]
    return any(pattern in lowered for pattern in patterns)


def build_time_response(timezone_name: str) -> str:
    timezone_aliases = {
        "Asia/Calcutta": "Asia/Kolkata",
    }
    resolved_timezone = timezone_aliases.get(timezone_name, timezone_name)
    try:
        now = datetime.now(ZoneInfo(resolved_timezone))
    except Exception:
        now = datetime.now()
    time_text = now.strftime("%I:%M %p").lstrip("0")
    date_text = now.strftime("%A, %d %B %Y")
    return f"The current time is {time_text} and today's date is {date_text}."


def init_chat_db(db_path: str) -> None:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        connection = _connect_db(path)
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()
        connection.close()
    except sqlite3.Error:
        # In restricted environments, SQLite writes may be blocked.
        pass


def save_chat_message(db_path: str, role: str, content: str) -> None:
    try:
        connection = _connect_db(db_path)
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO messages (role, content) VALUES (?, ?)",
            (role, content),
        )
        connection.commit()
        connection.close()
    except sqlite3.Error:
        pass


def load_chat_history(db_path: str, limit: int = 20) -> list[dict]:
    try:
        connection = _connect_db(db_path)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT role, content, created_at
            FROM messages
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        connection.close()
    except sqlite3.Error:
        return []

    history = []
    for row in reversed(rows):
        history.append(
            {
                "role": row["role"],
                "content": row["content"],
                "created_at": row["created_at"],
            }
        )
    return history


def _connect_db(db_path: str | Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA journal_mode=MEMORY")
    connection.execute("PRAGMA temp_store=MEMORY")
    connection.execute("PRAGMA synchronous=NORMAL")
    return connection
