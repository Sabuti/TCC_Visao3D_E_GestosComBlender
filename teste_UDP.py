# hand_detector_sender.py
# Requisitos: mediapipe, opencv-python, numpy
import cv2
import mediapipe as mp
import numpy as np
import socket
import json
import time
from collections import deque

# Config
BLENDER_IP = "127.0.0.1"   # se Blender estiver na mesma máquina
BLENDER_PORT = 5005

# UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Helper: calcula distância euclidiana
def dist(a, b):
    return np.linalg.norm(np.array(a) - np.array(b))

# Conta dedos estendidos (simples heurística)
# landmark: lista de 21 (x,y,z) normalizados do mediapipe
def count_fingers(landmarks):
    # índices da ponta e do pip para polegar e dedos
    tips_ids = [4, 8, 12, 16, 20]
    pip_ids = [2, 6, 10, 14, 18]  # usaremos para comparação simples
    count = 0
    # comparar a coordenada y (em imagem) — atenção: origem (0,0) em top-left
    for tip, pip in zip(tips_ids[1:], pip_ids[1:]):  # dedos (não polegar)
        if landmarks[tip][1] < landmarks[pip][1]:  # tip acima do pip => estendido
            count += 1
    # polegar (comparar x porque polegar abre lateralmente)
    # se mão direita vs esquerda pode precisar de flip; aqui é heurístico:
    if landmarks[4][0] > landmarks[3][0]:  # polegar "para direita" => aberto
        count += 1
    return count

# Detecta pinch (polegar + indicador próximos)
def is_pinching(landmarks, threshold=0.05):
    return dist(landmarks[4][:2], landmarks[8][:2]) < threshold

# Detecta punho (muitas pontas abaixo dos pips)
def is_fist(landmarks):
    # se menos de 2 dedos estendidos => punho
    return count_fingers(landmarks) <= 1

# Detecta palma aberta
def is_open_palm(landmarks):
    return count_fingers(landmarks) >= 4

# Detecta swipe baseado no movimento do centro da mão em últimas frames
centroids = deque(maxlen=6)
def detect_swipe():
    if len(centroids) < 4:
        return None
    dx = centroids[-1][0] - centroids[0][0]
    dy = centroids[-1][1] - centroids[0][1]
    if abs(dx) > 0.25 and abs(dx) > abs(dy):
        return "swipe_right" if dx > 0 else "swipe_left"
    if abs(dy) > 0.25 and abs(dy) > abs(dx):
        return "swipe_down" if dy > 0 else "swipe_up"
    return None

# Envia mensagem ao Blender (JSON)
def send_command(cmd_name, payload=None, value=None):
    msg = {"cmd": cmd_name, "payload": payload or {}, "value": value}
    data = json.dumps(msg).encode("utf-8")
    sock.sendto(data, (BLENDER_IP, BLENDER_PORT))

# Main capture
cap = cv2.VideoCapture(0)
with mp_hands.Hands(
    model_complexity=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6,
    max_num_hands=1,
) as hands:
    last_sent = 0
    last_gesture = None
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        h, w, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        gesture = None
        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            # convert landmarks to list of (x_px, y_px, z)
            lm = []
            for lm_item in hand.landmark:
                lm.append((lm_item.x, lm_item.y, lm_item.z))
            # centroid normalizado (média dos pontos)
            cx = np.mean([p[0] for p in lm])
            cy = np.mean([p[1] for p in lm])
            centroids.append((cx, cy))
            swipe = detect_swipe()
            if swipe:
                gesture = swipe
            elif is_pinching(lm, threshold=0.06):
                gesture = "girar_z"  # exemplo de ação contínua
                value = 40.1  # valor de giro
            elif is_fist(lm):
                gesture = "movex_x"
                value = 10.0  # valor de movimento
            elif is_open_palm(lm):
                gesture = "abrir_menu"
            else:
                c = count_fingers(lm)
                if c == 2:
                    gesture = "zoom_in"
                elif c == 3:
                    gesture = "zoom_out"
                elif c == 4: # FALTA TESTAR
                    gesture = "teste_mudar_modo" 

            # Desenhar landmarks
            mp_drawing.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

            # enviar posição do centro e profundidade aproximada
            payload = {"cx": cx, "cy": cy, "z_mean": float(np.mean([p[2] for p in lm]))}
            # enviar somente quando o gesto muda ou a cada 0.5s para reduzir spam
            now = time.time()
            if gesture != last_gesture or now - last_sent > 0.5:
                send_command(gesture, payload, value)
                last_sent = now
                last_gesture = gesture

            cv2.putText(frame, gesture, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        cv2.imshow("Hand Detector", frame)
        key = cv2.waitKey(1)
        if key & 0xFF == 27:  # ESC para sair
            break

cap.release()
cv2.destroyAllWindows()