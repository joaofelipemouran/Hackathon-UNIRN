import boto3
import os
from dotenv import load_dotenv

load_dotenv()

class AWSManager:
	def __init__(self):
		self.s3 = boto3.client('s3',
		aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
		aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
		region_name=os.gentenv('AWS_REGION')
	
		)
		self.bucket = os.getenv()
	def upload_foto(self,,):
		try:
			self.s3.upload_file(self.bucket,)
			return f"https://{self.bucket}.s3.amazonaws.com/{nome_s3}"
		except Exception as e:
			print(f"Erro no S3: {e}")
			return None

