import bpy
import socket
import json
import mathutils
import threading
import time
import queue

PORT = 5005
vel_base = 0.6
vel_corrente = vel_base
gravidade_ativa = True
chao_y = 1   # altura do "chão" no mapa https://sketchfab.com/3d-models/invasion-map-miniroyaleio-89f52d6ee9344cc48060076c222ad40b

ultimo_comando_tempo = {}
DEBOUNCE_RAPIDO = 0.15
DEBOUNCE_LENTO = 1.0
comandos_pendentes = queue.Queue()

def agora(): return time.time()

def pode_executar(cmd):
    t = agora()
    ultimo = ultimo_comando_tempo.get(cmd, 0)
    intervalo = DEBOUNCE_RAPIDO if cmd.startswith("olhar_") or cmd.startswith("mover_") else DEBOUNCE_LENTO
    if t - ultimo >= intervalo:
        ultimo_comando_tempo[cmd] = t
        return True
    return False

def get_camera():
    return bpy.data.objects.get("Camera")

# ============================================================
# === COLISÃO DA CÂMERA (raycast + tolerância de distância) ===
# ============================================================

DISTANCIA_MIN = 0.5   # distância mínima antes da colisão

def pode_mover(nova_pos):
    cam = get_camera()
    if not cam:
        return True

    origem = cam.location
    direcao = (nova_pos - origem)
    dist = direcao.length

    if dist < 0.0001:
        return True

    direcao = direcao.normalized()

    # depsgraph correto
    depsgraph = bpy.context.evaluated_depsgraph_get()

    # === Chamada correta para Blender 3.x / 4.x ===
    result, hit_loc, normal, index, obj, matrix = bpy.context.scene.ray_cast(
        depsgraph,
        origin=origem,
        direction=direcao,
        distance=dist + DISTANCIA_MIN
    )

    if result:
        return False

    return True

# =============================
# === MOVIMENTO COM COLISÃO ===
# =============================

def mover_frente():
    cam = get_camera()
    if not cam: 
        return

    frente = cam.matrix_world.to_quaternion() @ mathutils.Vector((0, 0, -1))
    nova_pos = cam.location + frente * vel_corrente

    # --- Teste de colisão ---
    if pode_mover(nova_pos):
        cam.location = nova_pos
    # else:
    #     print("Movimento bloqueado por colisão.")


def olhar_delta(dx, dy):
    cam = get_camera()
    if not cam: return
    e = cam.rotation_euler
    e.x += dy
    e.z += dx

def alternar_velocidade():
    global vel_corrente
    vel_corrente = vel_base * 2.5 if vel_corrente == vel_base else vel_base
    print("Velocidade:", vel_corrente)

def alternar_gravidade():
    global gravidade_ativa
    gravidade_ativa = not gravidade_ativa
    print("Gravidade:", "Ativa" if gravidade_ativa else "Desativada")

def aplicar_gravidade():
    if not gravidade_ativa: return
    cam = get_camera()
    if not cam: return
    if cam.location.z > chao_y:
        nova_pos = cam.location.copy()
        nova_pos.z -= 0.05

        if pode_mover(nova_pos):  # gravidade também respeita colisão
            cam.location = nova_pos


def executar(cmd):
    if not pode_executar(cmd): return
    if cmd == "mover_frente": mover_frente()
    elif cmd == "olhar_direita": olhar_delta(-0.1, 0)
    elif cmd == "olhar_esquerda": olhar_delta(0.1, 0)
    elif cmd == "olhar_cima": olhar_delta(0, 0.1)
    elif cmd == "olhar_baixo": olhar_delta(0, -0.1)
    elif cmd == "alternar_velocidade": alternar_velocidade()
    elif cmd == "mudar_gravidade": alternar_gravidade()

def processar():
    while not comandos_pendentes.empty():
        cmd = comandos_pendentes.get()
        try:
            executar(cmd)
        except Exception as e:
            print("Erro ao executar comando:", e)
    aplicar_gravidade()

def _tick():
    processar()
    return 0.05

def servidor_udp():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(("0.0.0.0", PORT))
    except OSError as e:
        print("Erro ao abrir porta UDP:", e)
        return
    print(f"Servidor UDP escutando em 0.0.0.0:{PORT}")
    sock.setblocking(False)
    while True:
        try:
            data, _ = sock.recvfrom(1024)
            comando = json.loads(data.decode())
            cmd = comando.get("cmd", "")
            comandos_pendentes.put(cmd)
        except BlockingIOError:
            pass
        except Exception as e:
            print("Erro no UDP:", e)
        time.sleep(0.01)

wm = bpy.context.window_manager
if not wm.get("_udp_thread_started"):
    t = threading.Thread(target=servidor_udp, daemon=True)
    t.start()
    wm["_udp_thread_started"] = True
    print("Servidor UDP iniciado.")
else:
    print("Servidor UDP já está rodando.")

bpy.app.timers.register(_tick, persistent=True)