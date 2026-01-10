import pytest

from local_o_vps import entorno
from variables_api_db import VariablesApiController, parse_boolean_value


def test_correr_workana_script_variable():
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

        print("🧪 [ETAPA 3] Buscando variable 'correr_workana_script'...")
        connection = controller._connection
        if connection is None:
            message = "⚠️ Conexión no disponible al intentar consultar la tabla 'variables'."
            print(message)
            pytest.skip(message)
        cursor = connection.cursor()
        cursor.execute(
            "SELECT value FROM variables WHERE name = ? LIMIT 1",
            ("correr_workana_script",),
        )
        result = cursor.fetchone()

        if not result:
            print(
                "❌ No se encontró la variable 'correr_workana_script' en la tabla 'variables'."
            )
            pytest.fail(
                "La variable 'correr_workana_script' no existe en la base de variables."
            )

        raw_value = str(result[0]).strip()
        parsed_value = parse_boolean_value(raw_value)
        print(f"✅ Variable encontrada. Valor crudo: '{raw_value}'.")
        print(f"✅ Valor interpretado (booleano): {parsed_value}.")

        print("🧪 [ETAPA 4] Validando lectura vía controlador...")
        controller_value = controller.ScriptMustRun
        print(f"✅ Valor devuelto por ScriptMustRun: {controller_value}.")

        assert (
            controller_value == parsed_value
        ), "El valor leído difiere entre la consulta directa y el controlador."
    finally:
        controller.CloseConnection()
