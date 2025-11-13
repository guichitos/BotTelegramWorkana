# monitor_workana/revisar_trabajos_en_workana.py
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urlencode

# Ensure local imports resolve
sys.path.append(os.path.dirname(__file__))

from local_o_vps import entorno
from workana_flag_manager import debe_ejecutarse
from telegram_flag_manager import gestionar_desde_telegram
from run_scraper_and_store import Run as RunScraper 
from workana_url import build_workana_url

# New: DB controller for original schema
from projects_db import proyectosDatabase


def VerifyConnection(db: proyectosDatabase) -> None:
    """Lightweight read to confirm DB access."""
    try:
        _ = db.get_recent(limit=1)
        print("Conexión a la base de datos verificada.")
    except Exception as ex:
        print(f"No se pudo verificar la conexión a la base de datos: {ex}")


def main():
    
    print("Ejecutado: ", datetime.now().strftime("%H:%M:%S"))
    gestionar_desde_telegram(entorno)

    if entorno not in ["local", "vps"]:
        print("Entorno no reconocido. Debe ser 'local' o 'vps'.")
        return

    if not debe_ejecutarse():
        print("La variable indica que NO debe ejecutarse el script.")
        return

    db = proyectosDatabase()
    VerifyConnection(db)


    url = build_workana_url()
    print(f"URL de Workana construida: {url}")

    try:

        try:
            # Run the scraper and store results
            cantidad = RunScraper(url)

        except TypeError:
            cantidad = 0
            print("❌ Error: La función RunScraper devolvió None en lugar de un entero.")
        ahora = datetime.now()
        print(f"Script ejecutado correctamente a las {ahora} — {cantidad} proyectos insertados/actualizados.")

        log_path = os.path.join(os.path.dirname(__file__), "ultima_ejecucion.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"Ejecutado a las {ahora} — {cantidad} proyectos insertados/actualizados.")

    except Exception as ex:
        print(f"Error ejecutando el scraper: {ex}")

if __name__ == "__main__":
    main()
