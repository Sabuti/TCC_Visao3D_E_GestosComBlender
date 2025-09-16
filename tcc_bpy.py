import bpy
import socket
import threading
import json

def start_system():
    i = 0
    while i < len(bpy.data.objects):
        if bpy.data.objects[i].name != "Camera" and bpy.data.objects[i].name != "Light":
            print(f"Na posicao {i} tem o {bpy.data.objects[i].name}")
            pos_objeto = i # considerando que só tem 1 objeto criado, fora Camera e Light
        i += 1
        
    name_objeto = bpy.data.objects[pos_objeto].name
    return name_objeto

def executar_comando(comando):
    if comando["acao"] == "girar_z":
        objeto.rotation_euler[2] += float(comando["valor"])
    elif comando["acao"] == "mover_x":
        objeto.location.x += float(comando["valor"])
    elif comando["acao"] == "abrir_menu":
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                override = {'area': area, 'region': area.regions[-1], 'space_data': area.spaces.active}
                bpy.ops.wm.call_menu(override, name="VIEW3D_MT_tools")
                break
    # Adicione mais ações conforme necessário

def servidor_socket():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('localhost', 5050))
    s.listen(1)
    print("Servidor do Blender aguardando comandos...")

    while True:
        conn, addr = s.accept()
        data = conn.recv(1024)
        try:
            comando = json.loads(data.decode())
            print("Recebido:", comando)
            executar_comando(comando)
        except Exception as e:
            print("Erro ao processar comando:", e)
        conn.close()

obj_name = start_system() # pra pegar qual é o objeto
objeto = bpy.data.objects.get(obj_name)  # Para definir o objeto a manipular
thread = threading.Thread(target=servidor_socket, daemon=True) # Criar a thread do servidor (uma vez só)
thread.start()
