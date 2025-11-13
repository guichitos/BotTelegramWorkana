# monitor_workana/config_variables_api_db.py
import mariadb
from local_o_vps import entorno

class VariablesApiController:
    def __init__(self, environment: str):
        self._environment = environment
        self._connection = self._connect()

    def _get_configuration(self) -> dict:
        if self._environment == "local":
            return {
                "host": "127.0.0.1",
                "port": 3306,
                "database": "variables_api",
                "user": "root",
                "password": ""
            }
        else:
            return {
                "host": "127.0.0.1",
                "port": 3306,
                "database": "admin_variables_api",
                "user": "admin_variables_user",
                "password": "passdeuser_proy_DB_25"
            }

    def _connect(self) -> mariadb.Connection:
        return mariadb.connect(**self._get_configuration())

    @property
    def ScriptMustRun(self) -> bool:
        try:
            cursor = self._connection.cursor()
            cursor.execute("SELECT value FROM variables WHERE name = 'correr_workana_script' LIMIT 1")
            result = cursor.fetchone()
            if result:
                return result[0].strip().lower() in ["1", "true", "t", "yes"]
            return False
        except mariadb.Error as e:
            print(f"❌ Error al consultar la variable de ejecución: {e}")
            return False
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

    def StartScraping(self) -> bool:
        return self._update_execution_variable("true")

    def StopScraping(self) -> bool:
        return self._update_execution_variable("false")

    def _update_execution_variable(self, value: str) -> bool:
        try:
            cursor = self._connection.cursor()
            cursor.execute(
                "UPDATE variables SET value = ? WHERE name = 'correr_workana_script'",
                (value,)
            )
            self._connection.commit()
            return True
        except mariadb.Error as e:
            print(f"❌ Error al actualizar variable de ejecución: {e}")
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
    if controller._update_execution_variable("true" if initial_state else "false"):
        print("✅ Estado restaurado correctamente")
    else:
        print("❌ No se pudo restaurar el estado")

    print("🔎 Estado final:", "✅ YES" if controller.ScriptMustRun else "❌ NO")

    controller.CloseConnection()