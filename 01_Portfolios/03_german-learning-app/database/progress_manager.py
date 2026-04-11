import json
import os
from datetime import datetime, date

PROGRESS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'user_progress.json')


def _load():
    if not os.path.exists(PROGRESS_FILE):
        return {"total_xp": 0, "streak": 0, "last_session": None, "completed_lessons": {}}
    with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def _save(data):
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_progress():
    return _load()


def complete_lesson(lesson_id, xp_earned, score_pct):
    data = _load()
    today = date.today().isoformat()

    if data["last_session"] != today:
        yesterday = (date.today().replace(day=date.today().day - 1)).isoformat() if date.today().day > 1 else None
        if data["last_session"] == yesterday:
            data["streak"] += 1
        else:
            data["streak"] = 1
        data["last_session"] = today

    data["total_xp"] += xp_earned
    data["completed_lessons"][lesson_id] = {
        "xp": xp_earned,
        "score_pct": score_pct,
        "completed_at": datetime.now().isoformat()
    }
    _save(data)
    return data


def is_lesson_completed(lesson_id):
    data = _load()
    return lesson_id in data.get("completed_lessons", {})


def get_lesson_score(lesson_id):
    data = _load()
    lesson_data = data.get("completed_lessons", {}).get(lesson_id)
    return lesson_data.get("score_pct", 0) if lesson_data else 0
