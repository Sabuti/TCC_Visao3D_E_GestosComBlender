import cv2
import mediapipe as mp
import math
# Inicialização do MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils
def teste():
    # Função de teste para retornar uma string
    return "Teste de função"
    
# Mensagens para o total de dedos (0 a 10)
mensagens_total = {
    0: "Alexa apaga a Luz",
    1: "Alexa acenda a Luz",
    2: "Alexa Coloque Musica aleatória",
    3: "Alexa ligue o ar condicionado",
    4: "Alexa Troque a cor do Led",
    5: "Chama a Alexa",
    6: " ",
    7: "7 dedos",
    8: "8 dedos",
    9: "9 dedos",
    10: "10 dedos"
}



# Função para distância entre dois pontos
def distancia(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

# Função para contar dedos
def contar_dedos(landmarks):
    dedos = 0
    altura_palma = landmarks[0].y

    # Polegar: baseado na distância entre THUMB_TIP e INDEX_MCP
    thumb_tip = landmarks[4]
    thumb_ip = landmarks[3]
    thumb_cmc = landmarks[1]
    index_mcp = landmarks[5]

    # Distâncias
    dist_thumb_to_index = distancia((thumb_tip.x, thumb_tip.y), (index_mcp.x, index_mcp.y))
    dist_thumb_to_palm = distancia((thumb_tip.x, thumb_tip.y), (thumb_cmc.x, thumb_cmc.y))

    # Se estiver distante o suficiente do indicador e da base, conta como levantado
    if dist_thumb_to_index > 0.08 and dist_thumb_to_palm > 0.06:
        dedos += 1

    # Outros dedos: se a ponta está acima da junta intermediária
    tips = [8, 12, 16, 20]
    for i in tips:
        if landmarks[i].y < landmarks[i - 2].y:
            dedos += 1

    return dedos

# Função para distância entre as mãos
def calcular_distancia(p1, p2):
    return int(math.hypot(p2[0] - p1[0], p2[1] - p1[1]))

cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        break

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)
    total_dedos = 0
    pos_maos = []

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            dedos = contar_dedos(handLms.landmark)
            total_dedos += dedos

            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

            x = int(handLms.landmark[0].x * img.shape[1])
            y = int(handLms.landmark[0].y * img.shape[0])
            pos_maos.append((x, y))

    # Mensagem baseada no total de dedos
    mensagem_total = mensagens_total.get(total_dedos, "Mais de 10 dedos!? 🫣")
    cv2.rectangle(img, (10, 30), (480, 70), (0, 0, 0), -1)
    cv2.putText(img, mensagem_total, (20, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Distância entre mãos
    if len(pos_maos) == 2:
        dist = calcular_distancia(pos_maos[0], pos_maos[1])
        texto_dist = f"Distância entre as mãos: {dist} px"
        cv2.line(img, pos_maos[0], pos_maos[1], (255, 0, 0), 2)
        meio = ((pos_maos[0][0] + pos_maos[1][0]) // 2,
                (pos_maos[0][1] + pos_maos[1][1]) // 2)
        cv2.putText(img, texto_dist, meio,
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (50, 255, 50), 2)

    cv2.imshow("Detecção de Dedos Robusta", img)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()