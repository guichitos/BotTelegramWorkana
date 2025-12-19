"""Helpers to load general project configuration from a JSON file."""
from __future__ import annotations

import json
import os
from typing import Dict

DEFAULT_INTERVAL_MINUTES = 5
DEFAULT_MAX_USERS = 1
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config_settings.json")


def _default_settings() -> Dict[str, int]:
    return {
        "scrape_all_minutes": DEFAULT_INTERVAL_MINUTES,
        "user_skill_scan_minutes": DEFAULT_INTERVAL_MINUTES,
        "max_users": DEFAULT_MAX_USERS,
    }


def load_settings(config_path: str | None = None) -> Dict[str, int]:
    """Load general configuration values from JSON, falling back to defaults."""
    path = config_path or CONFIG_PATH
    defaults = _default_settings()

    if not os.path.exists(path):
        return defaults

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return defaults

    return {
        "scrape_all_minutes": int(data.get("scrape_all_minutes", DEFAULT_INTERVAL_MINUTES)),
        "user_skill_scan_minutes": int(data.get("user_skill_scan_minutes", DEFAULT_INTERVAL_MINUTES)),
        "max_users": int(data.get("max_users", DEFAULT_MAX_USERS)),
    }
