import socket
import json
import time

def enviar_comando(comando):
    try:
        s = socket.socket()
        s.connect(('localhost', 5050))
        s.send(json.dumps(comando).encode())
        s.close()
    except ConnectionRefusedError:
        print("Blender não está ouvindo no socket.")

# Exemplo de envio contínuo de comandos
id = 6
while id > 0:
    # comando = {"acao": "girar_z","valor": 0.1 } # girar em z
    if id == 4:
        comando = {"acao": "abrir_menu"}
        enviar_comando(comando)
    print(f"id = {id}")
    time.sleep(5)
    id -= 1
