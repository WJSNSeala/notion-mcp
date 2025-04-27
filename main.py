from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
import os

from pydantic import BaseModel

from notion_api_client import NotionAPIClient

load_dotenv()

# 환경 변수에서 API 키 가져오기
NOTION_PRIVATE_API_KEY = os.getenv("NOTION_PRIVATE_API_KEY")
if not NOTION_PRIVATE_API_KEY:
    raise ValueError("API_KEY not found in environment variables")
else:
    print("NOTION_PRIVATE_API_KEY found")

app = FastAPI()


class NotionPage(BaseModel):
    id: str
    title: str
    url: str
    created_time: str
    last_edited_time: str


class NotionPagesResponse(BaseModel):
    pages: List[NotionPage]
    total_count: int


# 의존성 주입을 위한 함수 - API 키를 직접 사용
async def get_notion_client():
    """Notion API 클라이언트를 생성하고 반환합니다."""
    if not NOTION_PRIVATE_API_KEY:
        raise HTTPException(status_code=401, detail="Notion API 토큰이 필요합니다")

    return NotionAPIClient(api_key=NOTION_PRIVATE_API_KEY)


@app.get("/notion/query-database/{database_id}", response_model=NotionPagesResponse)
async def query_notion_database(
        database_id: str,
        notion_client: NotionAPIClient = Depends(get_notion_client),
        filter_params: Optional[Dict[str, Any]] = None,
        page_size: int = 100
):
    """
    지정된 데이터베이스 ID를 사용하여 Notion API에 직접 요청을 보내고 결과를 파싱합니다.
    """
    try:
        # NotionAPIClient를 사용하여 데이터베이스 쿼리
        async with notion_client:  # 컨텍스트 매니저 활용
            response = await notion_client.query_database(
                database_id=database_id,
                filter_params=filter_params,
                page_size=page_size
            )

        pages = []

        for result in response.get("results", []):
            if result.get("object") == "page":
                # 제목 추출
                title = extract_title_from_page(result)

                # 페이지 정보 수집
                page = NotionPage(
                    id=result.get("id", ""),
                    title=title,
                    url=result.get("url", ""),
                    created_time=result.get("created_time", ""),
                    last_edited_time=result.get("last_edited_time", "")
                )
                pages.append(page)

        return NotionPagesResponse(
            pages=pages,
            total_count=len(pages)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying Notion database: {str(e)}")


# 모든 페이지를 가져오는 엔드포인트 (페이지네이션 자동 처리)
@app.get("/notion/query-database-all/{database_id}", response_model=NotionPagesResponse)
async def query_notion_database_all(
        database_id: str,
        notion_client: NotionAPIClient = Depends(get_notion_client),
        filter_params: Optional[Dict[str, Any]] = None
):
    """
    지정된 데이터베이스의 모든 페이지를 가져옵니다 (페이지네이션 자동 처리).
    """
    try:
        async with notion_client:
            response = await notion_client.query_database_all(
                database_id=database_id,
                filter_params=filter_params
            )

        pages = []

        for result in response.get("results", []):
            if result.get("object") == "page":
                # 제목 추출 로직
                title = extract_title_from_page(result)

                # 페이지 정보 수집
                page = NotionPage(
                    id=result.get("id", ""),
                    title=title,
                    url=result.get("url", ""),
                    created_time=result.get("created_time", ""),
                    last_edited_time=result.get("last_edited_time", "")
                )
                pages.append(page)

        return NotionPagesResponse(
            pages=pages,
            total_count=len(pages)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying all pages: {str(e)}")


def extract_title_from_page(page: Dict[str, Any]) -> str:
    """페이지 객체에서 제목을 추출하는 헬퍼 함수"""
    # 기본적으로 '이름' 프로퍼티에서 제목 찾기
    title_property = page.get("properties", {}).get("이름", {})

    # '이름' 프로퍼티가 없거나 title 타입이 아닌 경우
    if not title_property or title_property.get("type") != "title":
        # properties에서 title 타입의 프로퍼티 찾기
        for prop_name, prop_value in page.get("properties", {}).items():
            if prop_value.get("type") == "title":
                title_property = prop_value
                break

    # 제목 텍스트 추출
    if title_property and title_property.get("type") == "title":
        title_content = title_property.get("title", [])
        if title_content:
            return title_content[0].get("plain_text", "")

    return ""