import cv2
import time
import sys
from config_aws import AWSManager
from ia_processador import ProcessadorIA
import os
from dotenv import load_dotenv
load_dotenv()


# Tenta pegar do terminal, se não houver, pega do arquivo .env
usuario_alvo = sys.argv[1] if len(sys.argv) > 1 else os.getenv('USUARIO_PADRAO')

if not usuario_alvo:
    print("Erro: Usuário não definido no terminal nem no .env")
    sys.exit()

if len(sys.argv) < 2:
    print("Uso: python3 main.py <nome_do_usuario>")
    sys.exit()

usuario_alvo = sys.argv[1]
aws = AWSManager()
ia = ProcessadorIA()
cap = cv2.VideoCapture(0)

# Configuração 1080p para o Pi 5
cap.set(cv2.PROP_FRAME_WIDTH, 1920)
cap.set(cv2.PROP_FRAME_HEIGHT, 1080)

print(f"Monitorando para o usuário: {usuario_alvo}...")

while True:
    ret, frame = cap.read()
    if not ret: break

    # Analisa a expressão
    emocao, confianca = ia.analisar_expressao(frame)

    # Exibe no vídeo (útil para testes locais)
    cv2.putText(frame, f"User: {usuario_alvo} | {emocao}", (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow('Monitor InsightFace - Pi 5', frame)

    # Se detectar uma emoção forte ou ao pressionar 's'
    tecla = cv2.waitKey(1) & 0xFF
    if tecla == ord('s') or (emocao != "Sem rosto" and emocao != "Neutro"):
        id_captura = str(int(time.time()))
        nome_arquivo = f"captura_{id_captura}.jpg"

        # Salva localmente
        cv2.imwrite(nome_arquivo, frame)

        # Envia para S3 com pasta organizada por usuário
        caminho_s3 = f"usuarios/{usuario_alvo}/{nome_arquivo}"
        url = aws.upload_foto(nome_arquivo, caminho_s3)

        if url:
            # Registra no DynamoDB incluindo o campo 'usuario_vinculado'
            sucesso = aws.registrar_no_banco(id_captura, emocao, confianca, url, usuario_alvo)
            if sucesso:
                print(f"Captura enviada: {emocao} ({confianca:.2f}%)")

        time.sleep(5)

    if tecla == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()