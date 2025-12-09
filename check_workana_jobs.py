# monitor_workana/revisar_trabajos_en_workana.py
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List

# Ensure local imports resolve
sys.path.append(os.path.dirname(__file__))

from config_intervals import load_intervals
from local_o_vps import entorno
from projects_db import proyectosDatabase
from run_scraper_and_store import Run as RunScraper
from telegram_flag_manager import gestionar_desde_telegram
from user_skills_model import UserSkills
from workana_bot_database_model import WorkanaBotDatabase
from workana_flag_manager import debe_ejecutarse


def VerifyConnection(db: proyectosDatabase) -> None:
    """Lightweight read to confirm DB access."""
    try:
        _ = db.get_recent(limit=1)
        print("Conexión a la base de datos verificada.")
    except Exception as ex:
        print(f"No se pudo verificar la conexión a la base de datos: {ex}")


def scrape_all_projects() -> int:
    """Scrape Workana without filters and persist results."""
    url = "https://www.workana.com/jobs?language=es"
    print(f"[SCRAPER] Ejecutando scrape completo: {url}")
    return RunScraper(url)


def get_user_skills_map(db: WorkanaBotDatabase) -> Dict[int, List[str]]:
    """Return a mapping of user_id -> list of skills (normalized)."""
    skills_by_user: Dict[int, List[str]] = {}
    rows = UserSkills.GetAllUsersSkills(db)
    for user_id, skill_slug in rows:
        if user_id is None or skill_slug is None:
            continue
        normalized = str(skill_slug).strip().lower()
        if not normalized:
            continue
        skills_by_user.setdefault(int(user_id), []).append(normalized)
    return skills_by_user


def run_user_skill_scan(project_db: proyectosDatabase) -> None:
    """Search stored projects for every user's skills (DB-only)."""
    base_db = WorkanaBotDatabase()
    skill_map = get_user_skills_map(base_db)
    if not skill_map:
        print("[SKILLS] No hay usuarios con skills configuradas.")
        return

    for user_id, skills in skill_map.items():
        matches = project_db.search_by_skills(skills, limit=200)
        print(f"[SKILLS] Usuario {user_id}: {len(matches)} coincidencias en la BD.")


def schedule_loop(interval_scrape: int, interval_skill_scan: int) -> None:
    """Main scheduler loop to run tasks every configured minutes."""
    project_db = proyectosDatabase()
    VerifyConnection(project_db)

    next_scrape = datetime.now()
    next_skill_scan = datetime.now()

    try:
        while True:
            now = datetime.now()
            ran_task = False

            if now >= next_scrape:
                try:
                    inserted = scrape_all_projects()
                    print(f"[SCRAPER] Insertados/actualizados: {inserted}")
                except Exception as ex:
                    print(f"[SCRAPER] Error: {ex}")
                next_scrape = now + timedelta(minutes=interval_scrape)
                ran_task = True

            if now >= next_skill_scan:
                try:
                    run_user_skill_scan(project_db)
                except Exception as ex:
                    print(f"[SKILLS] Error: {ex}")
                next_skill_scan = now + timedelta(minutes=interval_skill_scan)
                ran_task = True

            if ran_task:
                proxima = min(next_scrape, next_skill_scan).strftime("%H:%M:%S")
                print(f"[SCHEDULE] Próxima ejecución programada a las {proxima}")

            time.sleep(5)
    except KeyboardInterrupt:
        print("Scheduler detenido manualmente.")


def main():
    print("Ejecutado: ", datetime.now().strftime("%H:%M:%S"))
    gestionar_desde_telegram(entorno)

    if entorno not in ["local", "laptop", "vps"]:
        print("Entorno no reconocido. Debe ser 'local', 'laptop' o 'vps'.")
        return

    if not debe_ejecutarse():
        print("La variable indica que NO debe ejecutarse el script.")
        return

    intervals = load_intervals()
    schedule_loop(
        interval_scrape=intervals.get("scrape_all_minutes", 5),
        interval_skill_scan=intervals.get("user_skill_scan_minutes", 5),
    )


if __name__ == "__main__":
    main()
