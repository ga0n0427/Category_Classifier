# config.py
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경변수 불러오기
MONGO_URI = os.getenv("MONGO_URI")
REDIS_URL = os.getenv("REDIS_URL")
MODEL_PATH = os.getenv("MODEL_PATH")
FASTAPI_NAVER_SERVER = os.getenv("FASTAPI_NAVER_SERVER")