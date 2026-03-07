from deepface import DeepFace
import cv2

class ProcessadorIA:
    def __init__(self):
        # Cache para não repetir o carregamento do modelo desnecessariamente
        self.modelo = "VGG-Face"

    def analisar_expressao(self, frame):
        try:
            resultados = DeepFace.analyze(
                img_path = frame,
                actions = ['emotion'],
                enforce_detection = False, # Não trava se não houver rosto
                detector_backend = 'opencv', # Backend mais rápido para o Pi
                silent = True
            )

            if resultados:
                emocao_dominante = resultados[0]['dominant_emotion']
                confianca = resultados[0]['emotion'][emocao_dominante]

                traducoes = {
                    'angry': 'Raiva', 'disgust': 'Nojo', 'fear': 'Medo',
                    'happy': 'Feliz', 'sad': 'Triste', 'surprise': 'Surpresa',
                    'neutral': 'Neutro'
                }

                return traducoes.get(emocao_dominante, emocao_dominante), confianca

            return "Sem rosto", 0.0

        except Exception as e:
            print(f"Erro na analise: {e}")
            return "Erro", 0.0