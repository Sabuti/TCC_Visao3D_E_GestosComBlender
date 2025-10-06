import cv2
import mediapipe as mp
import math

# Inicialização do MediaPipe
mp_hands = mp.solutions.hands
mp_face = mp.solutions.face_detection
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
face_detection = mp_face.FaceDetection(min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Função de distância
def distancia(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

# --- Funções para gestos ---
def eh_mindinho(landmarks):
    """Verifica se só o mindinho está levantado (apenas ele)"""
    
    # Verifica cada dedo (polegar, indicador, medio, anelar, mindinho)
    # Polegar - lógica diferente
    polegar = landmarks[4].x < landmarks[3].x if landmarks[4].x < landmarks[0].x else landmarks[4].x > landmarks[3].x
    
    # Outros dedos
    indicador = landmarks[8].y < landmarks[6].y
    medio = landmarks[12].y < landmarks[10].y
    anelar = landmarks[16].y < landmarks[14].y
    mindinho = landmarks[20].y < landmarks[18].y
    
    # Apenas mindinho levantado
    return (not polegar and not indicador and not medio and not anelar and mindinho)

def eh_dedao(landmarks):
    """Verifica se só o dedão está levantado (apenas ele)"""
    # Pontos dos dedos
    polegar = landmarks[4].x < landmarks[3].x if landmarks[4].x < landmarks[0].x else landmarks[4].x > landmarks[3].x
    indicador = landmarks[8].y < landmarks[6].y
    medio = landmarks[12].y < landmarks[10].y
    anelar = landmarks[16].y < landmarks[14].y
    mindinho = landmarks[20].y < landmarks[18].y
    
    # Apenas dedão levantado
    return (polegar and not indicador and not medio and not anelar and not mindinho)

def eh_indicador_medio(landmarks, face_center):
    """Verifica se indicador e anelar estão levantados (apenas eles) e aponta direção"""
    # Verifica quais dedos estão levantados
    polegar = landmarks[4].x < landmarks[3].x if landmarks[4].x < landmarks[0].x else landmarks[4].x > landmarks[3].x
    indicador = landmarks[8].y < landmarks[6].y
    medio = landmarks[12].y < landmarks[10].y
    anelar = landmarks[16].y < landmarks[14].y
    mindinho = landmarks[20].y < landmarks[18].y
    
    # Apenas indicador e anelar levantados
    if (not polegar and indicador and medio and not anelar and not mindinho):
        # Calcula direção em relação ao rosto
        ponto_medio_x = (landmarks[8].x + landmarks[16].x) / 2
        ponto_medio_y = (landmarks[8].y + landmarks[16].y) / 2
        
        dx = ponto_medio_x - face_center[0]
        dy = ponto_medio_y - face_center[1]
        
        # Define limiar para considerar movimento
        limiar = 0.05
        
        if abs(dx) > abs(dy):
            return "Direita" if dx > limiar else "Esquerda" if dx < -limiar else "Centro"
        else:
            return "Baixo" if dy > limiar else "Cima" if dy < -limiar else "Centro"
    
    return None

def eh_indicador_mindinho(landmarks):
    """Verifica se indicador e o mindinho estão levantados (apenas eles)"""
    # Verifica quais dedos estão levantados
    polegar = landmarks[4].x < landmarks[3].x if landmarks[4].x < landmarks[0].x else landmarks[4].x > landmarks[3].x
    indicador = landmarks[8].y < landmarks[6].y
    medio = landmarks[12].y < landmarks[10].y
    anelar = landmarks[16].y < landmarks[14].y
    mindinho = landmarks[20].y < landmarks[18].y
    
    # Apenas indicador e mindinho levantados
    return (not polegar and indicador and not medio and not anelar and mindinho)

def posicao_indicador(landmarks):
    """Retorna posição absoluta do indicador (apenas quando só ele está levantado)"""
    # Verifica se apenas o indicador está levantado
    polegar = landmarks[4].x < landmarks[3].x if landmarks[4].x < landmarks[0].x else landmarks[4].x > landmarks[3].x
    indicador = landmarks[8].y < landmarks[6].y
    medio = landmarks[12].y < landmarks[10].y
    anelar = landmarks[16].y < landmarks[14].y
    mindinho = landmarks[20].y < landmarks[18].y
    
    if (not polegar and indicador and not medio and not anelar and not mindinho):
        return (landmarks[8].x, landmarks[8].y)
    return None

def mao_aberta(landmarks):
    """Todos os dedos levantados"""
    polegar = landmarks[4].x < landmarks[3].x if landmarks[4].x < landmarks[0].x else landmarks[4].x > landmarks[3].x
    indicador = landmarks[8].y < landmarks[6].y
    medio = landmarks[12].y < landmarks[10].y
    anelar = landmarks[16].y < landmarks[14].y
    mindinho = landmarks[20].y < landmarks[18].y
    
    return all([polegar, indicador, medio, anelar, mindinho])

def mao_fechada(landmarks):
    """Todos os dedos abaixados (punho fechado)"""
    polegar = landmarks[4].x > landmarks[3].x if landmarks[4].x < landmarks[0].x else landmarks[4].x < landmarks[3].x
    indicador = landmarks[8].y > landmarks[6].y
    medio = landmarks[12].y > landmarks[10].y
    anelar = landmarks[16].y > landmarks[14].y
    mindinho = landmarks[20].y > landmarks[18].y
    
    return all([polegar, indicador, medio, anelar, mindinho])

# --- Captura de vídeo ---
cap = cv2.VideoCapture(0)

# Contador para mãos detectadas
contador_maos = 0

while True:
    success, img = cap.read()
    if not success:
        break

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result_hands = hands.process(img_rgb)
    result_face = face_detection.process(img_rgb)

    face_center = (0.5, 0.5)  # padrão no meio da tela
    if result_face.detections:
        # Pega apenas o primeiro rosto detectado
        detection = result_face.detections[0]
        bbox = detection.location_data.relative_bounding_box
        h, w, _ = img.shape
        face_center = (bbox.xmin + bbox.width / 2, bbox.ymin + bbox.height / 2)
        cv2.rectangle(img, (int(bbox.xmin * w), int(bbox.ymin * h)),
                      (int((bbox.xmin + bbox.width) * w), int((bbox.ymin + bbox.height) * h)),
                      (0, 255, 0), 2)
        
        # Desenha ponto central do rosto
        cv2.circle(img, (int(face_center[0] * w), int(face_center[1] * h)), 5, (0, 255, 255), -1)

    if result_hands.multi_hand_landmarks:
        contador_maos = len(result_hands.multi_hand_landmarks)
        
        for i, handLms in enumerate(result_hands.multi_hand_landmarks):
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)
            
            # Identifica se é mão esquerda ou direita
            if result_hands.multi_handedness:
                handedness = result_hands.multi_handedness[i]
                lado = handedness.classification[0].label
                cv2.putText(img, f"{lado}", 
                           (int(handLms.landmark[0].x * img.shape[1]), 
                            int(handLms.landmark[0].y * img.shape[0]) - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            landmarks = handLms.landmark

            # --- Testes de gestos ---
            y_offset = 30
            if eh_mindinho(landmarks):
                cv2.putText(img, f"M{contador_maos}: Mindinho", (10, 100 + y_offset*i), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            elif eh_dedao(landmarks):
                cv2.putText(img, f"M{contador_maos}: Dedao", (10, 100 + y_offset*i), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 200, 0), 2)

            direcao = eh_indicador_medio(landmarks, face_center)
            if direcao and direcao != "Centro":
                cv2.putText(img, f"M{contador_maos}: Indicador+Anelar: {direcao}", 
                           (10, 130 + y_offset*i), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)

            pos_indicador = posicao_indicador(landmarks)
            if pos_indicador:
                h, w, _ = img.shape
                x_pos = int(pos_indicador[0] * w)
                y_pos = int(pos_indicador[1] * h)
                cv2.putText(img, f"M{contador_maos}: Indicador", 
                           (10, 160 + y_offset*i), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 0, 255), 2)
                # Desenha ponto na ponta do indicador
                cv2.circle(img, (x_pos, y_pos), 8, (200, 0, 255), -1)

            if mao_aberta(landmarks):
                cv2.putText(img, f"M{contador_maos}: Mao aberta", 
                           (10, 190 + y_offset*i), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            if mao_fechada(landmarks):
                cv2.putText(img, f"M{contador_maos}: Mao fechada", 
                           (10, 220 + y_offset*i), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            if eh_indicador_mindinho(landmarks):
                cv2.putText(img, f"M{contador_maos}: Indicador+Mindinho", 
                           (10, 250 + y_offset*i), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
            

    # Mostra contadores
    cv2.putText(img, f"Maos detectadas: {contador_maos}/2", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(img, f"Rosto detectado: {'Sim' if result_face.detections else 'Nao'}", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow("Reconhecimento de Gestos - TCC", img)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
