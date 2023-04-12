import os
import cloudinary
from fastapi import UploadFile
from cloudinary.uploader import upload
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

cloudinary.config(
  cloud_name = os.getenv('CLOUDINARY_NAME'),
  api_key = os.getenv('CLOUDINARY_API_KEY'),
  api_secret = os.getenv('CLOUDINARY_SECRET'),
  secure = True
)

def upload_image(file: UploadFile) -> dict:
    return upload(file.file)