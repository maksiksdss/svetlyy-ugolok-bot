import asyncio
import os
import sqlite3
import logging

from typing import Any, Awaitable, Callable, Dict

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.filters import Command
from aiogram.types import Message, ChatMemberUpdated, TelegramObject

logging.basicConfig(level=logging.INFO)

TOKEN = "8973821451:AAFN_egoEvrEEw2SunU28qjpXmDJ7wgVtS4"
ADMIN_ID = 5747252538

DB_PATH = "users.db"

bot = Bot(token=TOKEN)
dp = Dispatcher()


class BanCheckMiddleware(BaseMiddleware):
    """Полностью игнорирует любые сообщения от забаненных пользователей."""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if event.from_user and event.from_user.id == ADMIN_ID:
            return await handler(event, data)
        if event.chat and is_user_banned(event.chat.id):
            return
        return await handler(event, data)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            username TEXT,
            is_active INTEGER DEFAULT 1,
            is_banned INTEGER DEFAULT 0
        )
    """)
    try:
        conn.execute("ALTER TABLE users ADD COLUMN is_banned INTEGER DEFAULT 0")
        conn.commit()
    except sqlite3.OperationalError:
        pass
    conn.close()


def save_user(chat_id: int, username: str | None):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR IGNORE INTO users (chat_id, username) VALUES (?, ?)",
        (chat_id, username),
    )
    conn.commit()
    conn.close()


def get_active_users() -> list[int]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT chat_id FROM users WHERE is_active = 1").fetchall()
    conn.close()
    return [row[0] for row in rows]


def deactivate_user(chat_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE users SET is_active = 0 WHERE chat_id = ?", (chat_id,))
    conn.commit()
    conn.close()


def count_active_users() -> int:
    conn = sqlite3.connect(DB_PATH)
    n = conn.execute("SELECT COUNT(*) FROM users WHERE is_active = 1").fetchone()[0]
    conn.close()
    return n


def ban_user(chat_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE users SET is_banned = 1, is_active = 0 WHERE chat_id = ?", (chat_id,)
    )
    conn.commit()
    conn.close()


def unban_user(chat_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE users SET is_banned = 0, is_active = 1 WHERE chat_id = ?", (chat_id,)
    )
    conn.commit()
    conn.close()


def is_user_banned(chat_id: int) -> bool:
    conn = sqli
