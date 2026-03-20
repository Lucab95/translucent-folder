from __future__ import annotations

import json
from pathlib import Path

APP_DIR = Path.home() / '.config' / 'desktop-atelier'
STATE_PATH = APP_DIR / 'state.json'

DEFAULT_STATE = {
    'selected_video': '',
    'preferred_wallpaper_backend': 'hidamari',
}


def load_state() -> dict:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    if not STATE_PATH.exists():
        return DEFAULT_STATE.copy()
    try:
        data = json.loads(STATE_PATH.read_text())
    except (OSError, json.JSONDecodeError):
        return DEFAULT_STATE.copy()
    state = DEFAULT_STATE.copy()
    state.update({k: v for k, v in data.items() if k in state})
    return state


def save_state(state: dict) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    payload = DEFAULT_STATE.copy()
    payload.update(state)
    STATE_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True))
