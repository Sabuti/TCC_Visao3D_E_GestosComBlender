import bpy
import socket
import json

# Objeto que será manipulado
objeto = None

# Ação para iniciar o sistema e encontrar o objeto
def start_system():
    global objeto
    
    # Encontra o primeiro objeto que não seja 'Camera' ou 'Light'
    for obj in bpy.data.objects:
        if obj.name != "Camera" and obj.name != "Light":
            print(f"Objeto encontrado: {obj.name}")
            objeto = obj
            break

    if objeto:
        return True
    else:
        print("Nenhum objeto para manipular encontrado.")
        return False

# Função que executa os comandos recebidos
def executar_comando(comando):
    global objeto
    if not objeto:
        print("Erro: Objeto de manipulação não definido.")
        return
    
    cmd = comando.get("cmd")
    payload = comando.get("payload", {})

    if cmd == "girar_z":
        objeto.rotation_euler[2] += float(comando["value"])
    elif cmd == "mover_x":
        objeto.location.x += float(comando["value"])
    elif cmd == "zoom_in":
        cam = bpy.context.scene.camera.data
        cam.lens *= 1.2 # pra mais zoom
    elif cmd == "zoom_out":
        cam = bpy.context.scene.camera.data
        cam.lens *= 0.8 # pra menos zoom
    elif cmd == "teste_mudar_modo":
        bpy.ops.object.editmode_toggle() # TEM QUE TESTAR AINDA
    elif cmd == "abrir_menu":
        # ---- Abre a Toolbar na tela "Modeling" ----
        layout_screen = bpy.data.screens.get("Modeling")
        if not layout_screen:
            print("Tela 'Modeling' não encontrada.")
            return

        # Encontra a primeira área do tipo 3D View
        area_3d = next((a for a in layout_screen.areas if a.type == 'VIEW_3D'), None)
        if not area_3d:
            print("Nenhuma 3D View encontrada na tela 'Modeling'.")
            return

        # Procura a região TOOLS (toolbar lateral)
        region_tools = next((r for r in area_3d.regions if r.type == 'TOOLS'), None)
        if not region_tools:
            print("Nenhuma região TOOLS encontrada na área 3D.")
            return

        # Força a largura da toolbar para torná-la visível
        #region_tools.width = 300 # reclamou, então comentei
        #region_tools.tag_redraw()
        print("Toolbar aberta na tela 'Layout'.")

# Operador Modal para ouvir o socket UDP sem travar a interface
class SocketListenerModalOperator(bpy.types.Operator):
    bl_idname = "object.socket_listener"
    bl_label = "Blender Socket Listener"
    
    _timer = None
    _socket = None

    def modal(self, context, event):
        # O timer é o que fará a checagem a cada 0.1s
        if event.type == 'TIMER':
            if self._socket:
                try:
                    data, addr = self._socket.recvfrom(1024)
                    #print(f"Conexão aceita de: {addr}") # para debug
                    if data:
                        comando = json.loads(data.decode())
                        #print("Recebido:", comando) # para debug
                        executar_comando(comando)
                except BlockingIOError:
                    # Nenhuma mensagem nova, continua o loop
                    pass
                except Exception as e:
                    print("Erro ao processar comando:", e)
        
        # O operador pode ser finalizado com o 'ESC'
        if event.type in {'ESC'}:
            context.window_manager.event_timer_remove(self._timer)
            if self._socket:
                self._socket.close()
            print("Operador de Socket UDP finalizado.")
            return {'FINISHED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if not start_system():
            return {'CANCELLED'}

        # Inicia o socket no método invoke
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket.setblocking(False)
            self._socket.bind(('0.0.0.0', 5005))
            print("Servidor UDP do Blender aguardando comandos...")
        except Exception as e:
            print(f"Erro ao iniciar o servidor: {e}")
            return {'CANCELLED'}
        
        # Adiciona o timer para chamar o método modal
        self._timer = context.window_manager.event_timer_add(0.05, window=context.window)
        context.window_manager.modal_handler_add(self)
        
        return {'RUNNING_MODAL'}

# Funções de registro para o Blender
def register():
    try:
        bpy.utils.unregister_class(SocketListenerModalOperator)
    except RuntimeError:
        pass  # Classe ainda não registrada
    bpy.utils.register_class(SocketListenerModalOperator)

def unregister():
    bpy.utils.unregister_class(SocketListenerModalOperator)

register()
    # Roda Script
    # bpy.ops.object.socket_listener_modal_operator() (No console do Blender)