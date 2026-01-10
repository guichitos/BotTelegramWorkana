import os


def test_print_environment_variables():
    print("📦 Variables de entorno:")
    for key, value in os.environ.items():
        print(f"{key} = {value}")
