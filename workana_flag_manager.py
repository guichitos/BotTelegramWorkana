# workana_flag_manager.py
# Controla la ejecución del script Workana según la base de datos

from variables_api_db import VariablesApiController
from local_o_vps import entorno

config = VariablesApiController(entorno)

def debe_ejecutarse() -> bool:
    return config.ScriptMustRun


def debe_scrapear_general() -> bool:
    """Indica si debe ejecutarse el scraper general según la variable remota."""

    if not config.IsConnected:
        return False

    return config.GeneralScraperEnabled


def estado_remoto_scraper() -> bool | None:
    """Return the remote scraper flag when available, otherwise None."""

    if not config.IsConnected:
        return None
    return config.GeneralScraperEnabled

def activar_script() -> bool:
    return config.StartScraping()

def desactivar_script() -> bool:
    return config.StopScraping()

def tiene_conexion_config() -> bool:
    return config.IsConnected

def obtener_codigo_error_conexion() -> str:
    return config.ConnectionErrorCode or "VAR-DB-CONN-001"

if __name__ == "__main__":
    estado_actual = debe_ejecutarse()
    print(f"🔍 Estado actual de 'correr_workana_script': {estado_actual}")

    respuesta = input("¿Deseas cambiar el estado? (true/false/enter para no cambiar): ").strip().lower()

    if respuesta == "true":
        if activar_script():
            print("✅ Variable actualizada a TRUE.")
        else:
            print("❌ No se pudo activar el script.")
    elif respuesta == "false":
        if desactivar_script():
            print("✅ Variable actualizada a FALSE.")
        else:
            print("❌ No se pudo desactivar el script.")
    elif respuesta == "":
        print("🔁 Sin cambios realizados.")
    else:
        print("⚠️ Entrada inválida. Usa solo 'true', 'false' o presiona enter.")

    print(f"📌 Nuevo estado de 'correr_workana_script': {debe_ejecutarse()}")
