import cv2
from config_aws import AWSManager

aws = AWSManager()
cap = cv2.VideoCapture(0)

cap.set(cv2.PROP_FRAME_WIDTH,1920)
cap.set(cv2.PROP_FRAME_HEIGHT,1080)

while True:
	ret, frame = cap.read()
	if not ret: break

	cv2.imshow('Monitor 1080p',frame)

	if cv2.waitKey(1) & 0xFF == ord('s')
		print("Capturando e enviando...")
		
		nome_arquivo = "captura_hd.jpg"
		cv2.imwrite(nome_arquivo,frame,[int(cv2.IMWRITE_JPEG_QUALITY),90])
		
		url = aws.upload_foto(nome_arquivo,"foto/")
		if url:
			print(f""Sucesso!: {url}")
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

cap.release()
cv2.destroyALLWindoes()
