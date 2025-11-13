# monitor_workana/config_workana_bot_db.py

import mariadb
from local_o_vps import entorno

class WorkanaBotDatabase:
    def __init__(self):
        self._connection = None
    
    @property
    def IsConnected(self) -> bool:
        return self._connection is not None

    def _get_connection_config(self) -> dict:
        if entorno == "local":
            return {
                "host": "127.0.0.1",
                "port": 3306,
                "database": "proyectos_workana_db",
                "user": "root",
                "password": ""
            }
        else:
            return {
                "host": "127.0.0.1",
                "port": 3306,
                "database": "admin_proyectos_workana",
                "user": "admin_user_proyectos_db",
                "password": "passdeuser_proy_DB_25"
            }

    def connect(self):
        try:
            config = self._get_connection_config()
            self._connection = mariadb.connect(**config)
        except mariadb.Error as error:
            print(f"❌ Error connecting to Workana bot DB: {error}")
            self._connection = None

    def disconnect(self):
        if self._connection:
            self._connection.close()
            self._connection = None

    def execute_scalar(self, sql: str, params: tuple = ()) -> any:
        self.connect()
        if not self._connection:
            return None
        cursor = self._connection.cursor()
        cursor.execute(sql, params)
        result = cursor.fetchone()
        self.disconnect()
        return result[0] if result else None

    def execute_query(self, sql: str, params: tuple = ()) -> list:
        self.connect()
        if not self._connection:
            return []
        cursor = self._connection.cursor()
        cursor.execute(sql, params)
        result = cursor.fetchall()
        self.disconnect()
        return result

    def execute_non_query(self, sql: str, params: tuple = ()) -> bool:
        self.connect()
        if not self._connection:
            return False
        cursor = self._connection.cursor()
        try:
            cursor.execute(sql, params)
            self._connection.commit()
            return True
        except Exception as error:
            print(f"❌ SQL Execution Error: {error}")
            return False
        finally:
            self.disconnect()

# 🔽 MAIN PARA PRUEBA MANUAL DE LA CONEXIÓN
if __name__ == "__main__":
    db = WorkanaBotDatabase()
    
    print("Probando conexión...")
    db.connect()
    
    if db.IsConnected:
        print("✅ Conexión establecida correctamente.")
        
        # Consulta de prueba: verifica si existe alguna tabla
        sql = "SHOW TABLES"
        tablas = db.execute_query(sql)
        if tablas:
            print("Tablas encontradas en la base de datos:")
            for fila in tablas:
                print(f" - {fila[0]}")
        else:
            print("⚠️ No se encontraron tablas o error en la consulta.")
        
    else:
        print("❌ No se pudo conectar a la base de datos.")
    
    db.disconnect()
    print("Conexión cerrada.")
