import os


def _print_environment_variables() -> None:
    print("📦 Variables de entorno:")
    if not os.environ:
        print("⚠️ No hay variables de entorno disponibles.")
        return
    for key, value in os.environ.items():
        print(f"{key} = {value}")


def test_print_environment_variables():
    _print_environment_variables()


if __name__ == "__main__":
    print("▶️ Ejecutando impresión de variables de entorno...")
    _print_environment_variables()
