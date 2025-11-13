#telegram_flag_manager.py
from workana_flag_manager import activar_script, desactivar_script, debe_ejecutarse
from read_messages import leer_ultimo_mensaje_usuario
from local_o_vps import entorno

# Función principal de control desde Telegram
def gestionar_desde_telegram(entorno):
    ultimo = leer_ultimo_mensaje_usuario()
    if ultimo:
        texto = ultimo[1].strip().lower()
        if texto == "stop":
            desactivar_script(entorno)
        elif texto == "play":
            activar_script(entorno)

if __name__ == "__main__":
    gestionar_desde_telegram(entorno)

    if debe_ejecutarse():
        print("La variable está en TRUE. El script debe ejecutarse.")
    else:
        print("La variable está en FALSE. El script NO debe ejecutarse.")
