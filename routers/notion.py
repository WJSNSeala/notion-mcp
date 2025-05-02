from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any
from notion_api_client import NotionAPIClient
from models.notion_models import NotionPage, NotionPagesResponse
from core.config import get_notion_client

router = APIRouter(prefix="/notion", tags=["Notion"])

def extract_title_from_page(page: Dict[str, Any]) -> str:
    title_property = page.get("properties", {}).get("이름", {})
    if not title_property or title_property.get("type") != "title":
        for _, prop_value in page.get("properties", {}).items():
            if prop_value.get("type") == "title":
                title_property = prop_value
                break
    title_content = title_property.get("title", [])
    if title_content:
        return title_content[0].get("plain_text", "")
    return ""

@router.get("/query-database/{database_id}", response_model=NotionPagesResponse)
async def query_notion_database(
        database_id: str,
        notion_client: NotionAPIClient = Depends(get_notion_client),
        filter_params: Optional[Dict[str, Any]] = None,
        page_size: int = 100
):
    try:
        async with notion_client:
            response = await notion_client.query_database(
                database_id=database_id,
                filter_params=filter_params,
                page_size=page_size
            )
        pages = [
            NotionPage(
                id=r["id"],
                title=extract_title_from_page(r),
                url=r["url"],
                created_time=r["created_time"],
                last_edited_time=r["last_edited_time"]
            )
            for r in response.get("results", [])
            if r.get("object") == "page"
        ]
        return NotionPagesResponse(pages=pages, total_count=len(pages))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying Notion database: {str(e)}")

@router.get("/query-database-all/{database_id}", response_model=NotionPagesResponse)
async def query_notion_database_all(
        database_id: str,
        notion_client: NotionAPIClient = Depends(get_notion_client),
        filter_params: Optional[Dict[str, Any]] = None
):
    try:
        async with notion_client:
            response = await notion_client.query_database_all(
                database_id=database_id,
                filter_params=filter_params
            )
        pages = [
            NotionPage(
                id=r["id"],
                title=extract_title_from_page(r),
                url=r["url"],
                created_time=r["created_time"],
                last_edited_time=r["last_edited_time"]
            )
            for r in response.get("results", [])
            if r.get("object") == "page"
        ]
        return NotionPagesResponse(pages=pages, total_count=len(pages))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying all pages: {str(e)}")