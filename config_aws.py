import boto3
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class AWSManager:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        self.bucket_name = os.getenv('S3_BUCKET_NAME')

        self.dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        self.tabela = self.dynamodb.Table(os.getenv('DYNAMODB_TABLE'))

    def upload_foto(self, caminho_local, nome_no_s3):
        try:
            self.s3.upload_file(caminho_local, self.bucket_name, nome_no_s3)
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{nome_no_s3}"
            return url
        except Exception as e:
            print(f"Erro no S3: {e}")
            return None

    def registrar_no_banco(self, id_captura, emocao, confianca, url_s3, usuario):
        try:
            self.tabela.put_item(
                Item={
                    'id_captura': id_captura,
                    'usuario_vinculado': usuario, # CAMPO ESSENCIAL PARA O FILTRO
                    'emocao': emocao,
                    'confianca': f"{confianca:.2f}%",
                    'url_foto': url_s3,
                    'timestamp': str(datetime.now())
                }
            )
            return True
        except Exception as e:
            print(f"Erro no DynamoDB: {e}")
            return False