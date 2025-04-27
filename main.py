from fastapi import FastAPI
from httpx import AsyncClient

from dotenv import load_dotenv
import os

load_dotenv()

# 환경 변수에서 API 키 가져오기
NOTION_PRIVATE_API_KEY = os.getenv("NOTION_PRIVATE_API_KEY")
if not NOTION_PRIVATE_API_KEY:
    raise ValueError("API_KEY not found in environment variables")
else:
    print("NOTION_PRIVATE_API_KEY found")

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
