"""Helpers to load scraping intervals from a JSON config file."""
from __future__ import annotations

import json
import os
from typing import Dict

DEFAULT_INTERVAL_MINUTES = 5
DEFAULT_GENERAL_SCRAPER_ENABLED = True
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config_intervals.json")


def _to_bool(value, default: bool) -> bool:
    """Coerce JSON values (including strings) into a boolean."""

    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "t", "yes", "y"}:
            return True
        if normalized in {"0", "false", "f", "no", "n"}:
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return default


def load_intervals(config_path: str | None = None) -> Dict[str, int | bool]:
    path = config_path or CONFIG_PATH
    if not os.path.exists(path):
        return {
            "scrape_all_minutes": DEFAULT_INTERVAL_MINUTES,
            "user_skill_scan_minutes": DEFAULT_INTERVAL_MINUTES,
            "general_scraper_enabled": DEFAULT_GENERAL_SCRAPER_ENABLED,
        }

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {
            "scrape_all_minutes": DEFAULT_INTERVAL_MINUTES,
            "user_skill_scan_minutes": DEFAULT_INTERVAL_MINUTES,
            "general_scraper_enabled": DEFAULT_GENERAL_SCRAPER_ENABLED,
        }

    if "general_scraper_enabled" in data:
        print(
            "[CONFIG] 'general_scraper_enabled' en config_intervals.json ya no se usa; "
            "el scraper general se controla solo con la variable en BD."
        )

    return {
        "scrape_all_minutes": int(data.get("scrape_all_minutes", DEFAULT_INTERVAL_MINUTES)),
        "user_skill_scan_minutes": int(data.get("user_skill_scan_minutes", DEFAULT_INTERVAL_MINUTES)),
        "general_scraper_enabled": _to_bool(
            data.get("general_scraper_enabled", DEFAULT_GENERAL_SCRAPER_ENABLED),
            DEFAULT_GENERAL_SCRAPER_ENABLED,
        ),
    }
