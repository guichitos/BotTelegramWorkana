"""Helpers to load scraping intervals from a JSON config file."""
from __future__ import annotations

import json
import os
from typing import Dict

DEFAULT_INTERVAL_MINUTES = 5
DEFAULT_GENERAL_SCRAPER_ENABLED = True
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config_intervals.json")


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

    return {
        "scrape_all_minutes": int(data.get("scrape_all_minutes", DEFAULT_INTERVAL_MINUTES)),
        "user_skill_scan_minutes": int(data.get("user_skill_scan_minutes", DEFAULT_INTERVAL_MINUTES)),
        "general_scraper_enabled": bool(
            data.get("general_scraper_enabled", DEFAULT_GENERAL_SCRAPER_ENABLED)
        ),
    }
