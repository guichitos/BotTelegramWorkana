# monitor_workana/revisar_trabajos_en_workana.py
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Optional

# Ensure local imports resolve
sys.path.append(os.path.dirname(__file__))

from config_intervals import load_intervals
from local_o_vps import entorno
from projects_db import proyectosDatabase
from projects_db_manager import ProjectRepository
from run_scraper_and_store import Run as RunScraper
from telegram_flag_manager import gestionar_desde_telegram
from workana_flag_manager import (
    debe_ejecutarse,
    debe_scrapear_general,
    tiene_conexion_config,
)


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


STATE_FILE = "ultima_revision_skills.log"


def _load_last_skill_scan() -> Optional[datetime]:
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return datetime.fromisoformat(content) if content else None
    except Exception:
        return None


def _persist_last_skill_scan(ts: datetime) -> None:
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            f.write(ts.isoformat())
    except Exception as ex:
        print(f"[SKILLS] No se pudo escribir el estado de escaneo: {ex}")


def run_user_skill_scan(repo: ProjectRepository) -> None:
    """Evaluate stored projects against user skills and send Telegram alerts."""
    last_scan = _load_last_skill_scan()
    projects = repo.get_projects_for_skill_scan(since=last_scan, limit=200)

    if not projects:
        print("[SKILLS] No hay proyectos nuevos para revisar.")
        _persist_last_skill_scan(datetime.now())
        return

    repo.notify_users_for_projects(projects)
    _persist_last_skill_scan(datetime.now())


def schedule_loop(
    interval_scrape: int,
    interval_skill_scan: int,
) -> None:
    """Main scheduler loop to run tasks every configured minutes."""
    project_db = proyectosDatabase()
    repo = ProjectRepository()
    VerifyConnection(project_db)

    next_scrape = datetime.now()
    next_skill_scan = datetime.now()

    try:
        while True:
            now = datetime.now()
            ran_task = False

            if now >= next_scrape:
                run_scraper = debe_scrapear_general()

                if run_scraper:
                    try:
                        inserted = scrape_all_projects()
                        print(f"[SCRAPER] Insertados/actualizados: {inserted}")
                    except Exception as ex:
                        print(f"[SCRAPER] Error: {ex}")
                else:
                    reason = "por variable remota"
                    if not tiene_conexion_config():
                        reason = "por falta de conexión con la base de variables"
                    print(
                        f"[SCRAPER] Scraper general desactivado {reason}; se omite esta ejecución."
                    )
                next_scrape = now + timedelta(minutes=interval_scrape)
                ran_task = True

            if now >= next_skill_scan:
                try:
                    run_user_skill_scan(repo)
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
