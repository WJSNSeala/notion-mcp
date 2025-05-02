import os
from dotenv import load_dotenv
from fastapi import HTTPException
from notion_api_client import NotionAPIClient

load_dotenv()

NOTION_PRIVATE_API_KEY = os.getenv("NOTION_PRIVATE_API_KEY")

def get_notion_client():
    if not NOTION_PRIVATE_API_KEY:
        raise HTTPException(status_code=401, detail="Notion API 토큰이 필요합니다")
    return NotionAPIClient(api_key=NOTION_PRIVATE_API_KEY)