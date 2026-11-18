import json
import os
import logging
from datetime import datetime

from config import DATA_FILE, DATABASE_URL
from threading import RLock
_lock = RLock()
if DATABASE_URL:
    import psycopg
    from psycopg.types.json import Jsonb

def init_database():
    if DATABASE_URL:
        with psycopg.connect(DATABASE_URL) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS memory_users (user_id TEXT PRIMARY KEY, payload JSONB NOT NULL)")


logger = logging.getLogger(__name__)

# ==================== MA'LUMOTLAR OMBORI ====================

def load_data() -> dict:
    """Read persistent user records from PostgreSQL, or local JSON for development."""
    with _lock:
        if DATABASE_URL:
            with psycopg.connect(DATABASE_URL) as conn:
                return {uid: payload for uid, payload in conn.execute("SELECT user_id, payload FROM memory_users")}
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error("Database read error: %s", e)
                raise
        return {}


def save_data(data: dict) -> None:
    """Persist all users. PostgreSQL survives redeploys and new hosting accounts."""
    with _lock:
        if DATABASE_URL:
            with psycopg.connect(DATABASE_URL) as conn:
                with conn.cursor() as cur:
                    for uid, payload in data.items():
                        cur.execute("INSERT INTO memory_users (user_id, payload) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET payload = EXCLUDED.payload", (uid, Jsonb(payload)))
            return
        temp = DATA_FILE + ".tmp"
        with open(temp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(temp, DATA_FILE)


def import_legacy_json():
    """One-time safe import, never overwrite an existing cloud record."""
    if not DATABASE_URL or not os.path.exists(DATA_FILE):
        return 0
    with open(DATA_FILE, encoding="utf-8") as f:
        legacy = json.load(f)
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            for uid, payload in legacy.items():
                cur.execute("INSERT INTO memory_users (user_id, payload) VALUES (%s, %s) ON CONFLICT (user_id) DO NOTHING", (uid, Jsonb(payload)))
    return len(legacy)


def get_user(user_id: str) -> dict:
    """Foydalanuvchi ma'lumotlarini olish, agar yo'q bo'lsa yangi yaratish."""
    data = load_data()
    if user_id not in data:
        data[user_id] = {
            "folders": {},
            "contacts": {},
            "notes": {},
            "links": {},
            "schedules": {},
            "language": None,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
        }
        save_data(data)
    return data[user_id]


def update_user_field(user_id: str, field: str, value) -> None:
    """Foydalanuvchining bitta maydonini yangilash."""
    data = load_data()
    if user_id not in data:
        get_user(user_id)
        data = load_data()
    data[user_id][field] = value
    data[user_id]["last_activity"] = datetime.now().isoformat()
    save_data(data)


def get_user_lang(user_id: str) -> str:
    """Foydalanuvchi tilini olish."""
    user = get_user(user_id)
    return user.get("language") or "uz"


def update_user_activity(user_id: str) -> None:
    """Foydalanuvchi aktivligini yangilash."""
    data = load_data()
    if user_id in data:
        data[user_id]["last_activity"] = datetime.now().isoformat()
        save_data(data)


def get_user_stats() -> dict:
    """Umumiy foydalanuvchi statistikasini olish (admin uchun)."""
    data = load_data()
    total_users = 0
    active_today = 0
    active_weekly = 0

    for user_id, user_data in data.items():
        if user_id == "stats":
            continue
        total_users += 1
        last_activity = user_data.get("last_activity")
        if last_activity:
            try:
                last_seen = datetime.fromisoformat(last_activity)
                days_diff = (datetime.now() - last_seen).days
                if days_diff <= 1:
                    active_today += 1
                if days_diff <= 7:
                    active_weekly += 1
            except (ValueError, TypeError):
                pass

    return {
        "total_users": total_users,
        "active_today": active_today,
        "active_weekly": active_weekly,
    }
