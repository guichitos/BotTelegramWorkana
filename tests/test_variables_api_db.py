import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from local_o_vps import entorno
from variables_api_db import VariablesApiController, parse_boolean_value


def test_general_scraper_enabled_variable():
    print("🧪 [ETAPA 1] Inicializando controlador de variables API...")
    controller = VariablesApiController(entorno)

    try:
        print("🧪 [ETAPA 2] Verificando conexión a la base de variables...")
        if not controller.IsConnected:
            message = (
                "⚠️ No se pudo conectar a la base de variables; "
                f"código: {controller.ConnectionErrorCode}"
            )
            print(message)
            pytest.skip(message)

        print("✅ Conexión establecida correctamente.")

        print("🧪 [ETAPA 3] Verificando existencia de tabla 'variables'...")
        connection = controller._connection
        if connection is None:
            message = "⚠️ Conexión no disponible al intentar consultar la tabla 'variables'."
            print(message)
            pytest.skip(message)
        cursor = connection.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = DATABASE() AND table_name = ?",
            ("variables",),
        )
        table_result = cursor.fetchone()
        table_exists = bool(table_result and table_result[0])
        print(f"✅ Tabla 'variables' existe: {table_exists}.")
        if not table_exists:
            pytest.fail("La tabla 'variables' no existe en la base de datos.")

        print("🧪 [ETAPA 4] Buscando variable 'general_scraper_enabled'...")
        cursor.execute(
            "SELECT value FROM variables WHERE name = ? LIMIT 1",
            ("general_scraper_enabled",),
        )
        result = cursor.fetchone()

        if not result:
            print(
                "❌ No se encontró la variable 'general_scraper_enabled' en la tabla 'variables'."
            )
            pytest.fail(
                "La variable 'general_scraper_enabled' no existe en la base de variables."
            )

        raw_value = str(result[0]).strip()
        parsed_value = parse_boolean_value(raw_value)
        print(f"✅ Variable encontrada. Valor crudo: '{raw_value}'.")
        print(f"✅ Valor interpretado (booleano): {parsed_value}.")

        print("🧪 [ETAPA 5] Validando lectura vía controlador...")
        controller_value = controller.ScriptMustRun
        print(f"✅ Valor devuelto por ScriptMustRun: {controller_value}.")

        assert (
            controller_value == parsed_value
        ), "El valor leído difiere entre la consulta directa y el controlador."
    finally:
        controller.CloseConnection()
