# config_variables_api_db.py
import mariadb
import os
from dotenv import load_dotenv
from local_o_vps import entorno

load_dotenv()

class VariablesApiController:
    def __init__(self, environment: str):
        self._environment = environment
        self._connection = None
        self._connection_error = None
        self._connection_error_code = None
        self._connect()

    def _get_configuration(self) -> dict:
        if self._environment == "local":
            return {
                "host": os.getenv("LOCAL_DB_HOST", "127.0.0.1"),
                "port": int(os.getenv("LOCAL_DB_PORT", 3306)),
                "database": os.getenv("LOCAL_DB_NAME", "variables_api"),
                "user": os.getenv("LOCAL_DB_USER", "root"),
                "password": os.getenv("LOCAL_DB_PASS", ""),
            }
        if self._environment == "laptop":
            return {
                "host": os.getenv("LAPTOP_DB_HOST", "127.0.0.1"),
                "port": int(os.getenv("LAPTOP_DB_PORT", 3306)),
                "database": os.getenv("LAPTOP_DB_NAME", "variables_api"),
                "user": os.getenv("LAPTOP_DB_USER", "root"),
                "password": os.getenv("LAPTOP_DB_PASS", ""),
            }
        return {
            "host": os.getenv("VPS_DB_HOST", "127.0.0.1"),
            "port": int(os.getenv("VPS_DB_PORT", 3306)),
            "database": os.getenv("VPS_DB_NAME", "admin_variables_api"),
            "user": os.getenv("VPS_DB_USER", "admin_variables_user"),
            "password": os.getenv("VPS_DB_PASS", "default-fallback"),
        }

    def _connect(self) -> mariadb.Connection | None:
        """Intentar conectar con la base de datos evitando romper la ejecución."""
        try:
            self._connection = mariadb.connect(**self._get_configuration())
            self._connection_error_code = None
            return self._connection
        except mariadb.Error as e:
            self._connection = None
            self._connection_error = e
            self._connection_error_code = "VAR-DB-CONN-001"
            print(f"⚠️ No se pudo conectar a la base de datos de variables: {e}")
            return None

    def _get_boolean_variable(self, name: str, *, default_if_missing: bool = False) -> bool:
        try:
            if not self._connection:
                return False
            cursor = self._connection.cursor()
            cursor.execute("SELECT value FROM variables WHERE name = ? LIMIT 1", (name,))
            result = cursor.fetchone()
            if result:
                return str(result[0]).strip().lower() in ["1", "true", "t", "yes"]
            print(
                "⚠️ La variable '{name}' no existe en la base de variables; se asume {value}.".format(
                    name=name,
                    value="True" if default_if_missing else "False",
                )
            )
            return default_if_missing
        except mariadb.Error as e:
            print(f"❌ Error al consultar la variable '{name}': {e}")
            return False

    @property
    def ScriptMustRun(self) -> bool:
        return self._get_boolean_variable("correr_workana_script")

    @property
    def GeneralScraperEnabled(self) -> bool:
        # El scraper general comparte el mismo switch que el script principal
        return self._get_boolean_variable("correr_workana_script")

    @property
    def IsConnected(self) -> bool:
        try:
            if self._connection:
                cursor = self._connection.cursor()
                cursor.execute("SELECT 1")
                return True
            return False
        except mariadb.Error:
            return False

    @property
    def ConnectionErrorCode(self) -> str | None:
        return self._connection_error_code

    def StartScraping(self) -> bool:
        return self._update_execution_variable("correr_workana_script", "true")

    def StopScraping(self) -> bool:
        return self._update_execution_variable("correr_workana_script", "false")

    def EnableGeneralScraper(self) -> bool:
        return self._update_execution_variable("correr_workana_script", "true")

    def DisableGeneralScraper(self) -> bool:
        return self._update_execution_variable("correr_workana_script", "false")

    def _update_execution_variable(self, name: str, value: str) -> bool:
        if not self._connection:
            print("⚠️ No hay conexión a la base de datos para actualizar la variable.")
            return False
        try:
            cursor = self._connection.cursor()
            cursor.execute(
                "UPDATE variables SET value = ? WHERE name = ?",
                (value, name),
            )
            self._connection.commit()
            return True
        except mariadb.Error as e:
            print(f"❌ Error al actualizar la variable '{name}': {e}")
            return False

    def CloseConnection(self):
        if self._connection:
            self._connection.close()

if __name__ == "__main__":
    controller = VariablesApiController(entorno)

    # 🟡 Guardar estado inicial
    initial_state = controller.ScriptMustRun
    print("🔎 Estado inicial:", "✅ YES" if initial_state else "❌ NO")

    # ⏩ Activar
    print("⏩ Activando...")
    if controller.StartScraping():
        print("✅ Activado correctamente")
    else:
        print("❌ No se pudo activar")

    print("🔎 Estado después de activar:", "✅ YES" if controller.ScriptMustRun else "❌ NO")

    # ⏹️ Desactivar
    print("⏹️ Desactivando...")
    if controller.StopScraping():
        print("✅ Desactivado correctamente")
    else:
        print("❌ No se pudo desactivar")

    print("🔎 Estado después de desactivar:", "✅ YES" if controller.ScriptMustRun else "❌ NO")

    # 🔁 Restaurar estado inicial
    print("🔁 Restaurando estado inicial...")
    if controller._update_execution_variable(
        "correr_workana_script", "true" if initial_state else "false"
    ):
        print("✅ Estado restaurado correctamente")
    else:
        print("❌ No se pudo restaurar el estado")

    print("🔎 Estado final:", "✅ YES" if controller.ScriptMustRun else "❌ NO")

    controller.CloseConnection()
