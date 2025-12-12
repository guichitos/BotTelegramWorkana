"""Helpers to load scraping intervals from a JSON config file."""
from __future__ import annotations

import json
import os
from typing import Dict

DEFAULT_INTERVAL_MINUTES = 5
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config_intervals.json")


def load_intervals(config_path: str | None = None) -> Dict[str, int]:
    path = config_path or CONFIG_PATH
    if not os.path.exists(path):
        return {
            "scrape_all_minutes": DEFAULT_INTERVAL_MINUTES,
            "user_skill_scan_minutes": DEFAULT_INTERVAL_MINUTES,
        }

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {
            "scrape_all_minutes": DEFAULT_INTERVAL_MINUTES,
            "user_skill_scan_minutes": DEFAULT_INTERVAL_MINUTES,
        }

    if "general_scraper_enabled" in data:
        data.pop("general_scraper_enabled", None)
        print(
            "[CONFIG] 'general_scraper_enabled' en config_intervals.json ya no se usa; "
            "el scraper general se controla solo con la variable en BD."
        )

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
        except Exception as exc:  # pragma: no cover - best-effort cleanup
            print(
                "[CONFIG] No se pudo limpiar la clave 'general_scraper_enabled' del "
                f"archivo de configuración: {exc}"
            )

    return {
        "scrape_all_minutes": int(data.get("scrape_all_minutes", DEFAULT_INTERVAL_MINUTES)),
        "user_skill_scan_minutes": int(data.get("user_skill_scan_minutes", DEFAULT_INTERVAL_MINUTES)),
    }
