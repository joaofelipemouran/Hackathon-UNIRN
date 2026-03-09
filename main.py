import boto3
import os
import sys
import types
import time
import cv2
import numpy as np
from datetime import datetime
from deepface import DeepFace

# 1. PATCH DE COMPATIBILIDADE (Para Python 3.13)
# Simula o módulo 'imp' removido para evitar erro no TensorFlow/DeepFace
if 'imp' not in sys.modules:
    imp_mock = types.ModuleType('imp')
    imp_mock.acquire_lock = lambda: None
    imp_mock.release_lock = lambda: None
    imp_mock.find_module = lambda name, path=None: None
    sys.modules['imp'] = imp_mock
    print("[INFO] Módulo 'imp' emulado com sucesso.")

def capture_image(file_path):
    """Captura a imagem em HD com ajustes de nitidez e contraste via hardware."""
    print(f" Disparando câmera (HD 720p)...")
    # --sharpening aumenta a definição das sobrancelhas/olhos
    # --quality 100 garante que a foto no dashboard fique nítida
    command = (
        f"rpicam-still -o {file_path} --immediate --nopreview "
        f"--width 1280 --height 720 --quality 100 "
        f"--sharpening 2.0 --contrast 1.1"
    )
    os.system(command)

def improve_image(file_path):
    """Tratamento profissional de contraste (CLAHE) para reduzir erros Raiva vs Medo."""
    img = cv2.imread(file_path)
    if img is None:
        return False
    
    # Processamento no espaço de cor LAB para equalizar apenas a luz (brilho)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # CLAHE: clipLimit baixo evita ruído, tileGridSize captura microexpressões
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    
    img_output = cv2.merge((l, a, b))
    img_final = cv2.cvtColor(img_output, cv2.COLOR_LAB2BGR)
    
    # Sobrescreve o arquivo original com a versão tratada
    cv2.imwrite(file_path, img_final)
    return True

def process_cycle():
    """Executa um ciclo completo: Captura -> Melhora -> IA -> Nuvem."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"face_{timestamp}.jpg"
    
    try:
        # Passo 1: Captura
        capture_image(file_name)
        
        # Passo 2: Pré-processamento
        print("Melhorando qualidade visual e destaque facial...")
        if not improve_image(file_name):
            print(" Falha ao tratar imagem.")
            return

        # Passo 3: Análise DeepFace (SSD - Mais preciso que o OpenCV)
        print("Iniciando análise de emoção (Modo SSD - Alta Precisão)...")
        results = DeepFace.analyze(
            img_path=file_name, 
            actions=['emotion'], 
            enforce_detection=True, 
            detector_backend='ssd' # SSD resolve a confusão Raiva/Medo melhor que o OpenCV
        )
        
        emotion = results['dominant_emotion']
        s3_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{file_name}"

        # Passo 4: Upload S3 (Foto tratada)
        print(f"Resultado: {emotion.upper()}. Subindo para AWS...")
        s3_client.upload_file(file_name, S3_BUCKET_NAME, file_name)
        
        # Passo 5: Registro DynamoDB (Sincronizado com o Django)
        table.put_item(
            Item={
                'id_captura': timestamp,
                'emotion': emotion,
                's3_url': s3_url,
                'timestamp': str(datetime.now())
            }
        )
        print("✔ Ciclo finalizado! Dados disponíveis no Dashboard.")

    except Exception as e:
        print(f"⚠ Aviso: Falha na detecção facial (Rosto não visível ou escuro).")
    finally:
        # Limpa o arquivo local para não lotar o cartão SD
        if os.path.exists(file_name):
            os.remove(file_name)

if __name__ == "__main__":
    print("\n" + "="*40)
    print("  INSIGHTFACE: MONITORAMENTO ATIVADO")
    print("="*40)
    print("Pressione Ctrl+C para encerrar.\n")
    
    try:
        while True:
            process_cycle()
            # Aguarda 30 segundos para evitar superaquecimento no Pi 3
            print("\nAguardando 30 segundos para a próxima captura...")
            time.sleep(30)
    except KeyboardInterrupt:
        print("\nEncerrando monitoramento...")
