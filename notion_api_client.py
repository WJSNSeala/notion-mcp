from typing import Optional, Dict, Any

from httpx import AsyncClient


class NotionAPIClient:
    BASE_URL = "https://api.notion.com/v1"

    def __init__(self, api_key, version='2022-06-28'):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Notion-Version": version,
            "Content-Type": "application/json"
        }
        self.client = AsyncClient(timeout=30.0)  # 타임아웃 설정 추가

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """클라이언트 연결을 종료합니다."""
        await self.client.aclose()

    async def query_database(self, database_id: str, filter_params: Optional[Dict[str, Any]] = None,
                             sorts: Optional[list] = None, start_cursor: Optional[str] = None,
                             page_size: int = 100) -> Dict[str, Any]:
        """
        Notion 데이터베이스를 쿼리하여 결과를 반환합니다.

        Args:
            database_id: 쿼리할 데이터베이스의 ID
            filter_params: 쿼리 필터 (선택사항)
            sorts: 정렬 옵션 (선택사항)
            start_cursor: 페이지네이션 커서 (선택사항)
            page_size: 한 번에 가져올 결과 수 (기본값: 100)

        Returns:
            API 응답 결과를 딕셔너리 형태로 반환
        """
        url = f"{self.BASE_URL}/databases/{database_id}/query"

        # 요청 본문 구성
        payload = {}
        if filter_params:
            payload["filter"] = filter_params
        if sorts:
            payload["sorts"] = sorts
        if start_cursor:
            payload["start_cursor"] = start_cursor
        if page_size:
            payload["page_size"] = page_size

        response = await self.client.post(
            url=url,
            headers=self.headers,
            json=payload
        )

        # 응답 확인
        if response.status_code != 200:
            error_info = response.json()
            raise Exception(f"Notion API 요청 실패: {response.status_code}, {error_info}")

        return response.json()


# 모든 결과를 가져오는 헬퍼 메서드 (페이지네이션 처리)
async def query_database_all(self, database_id: str, filter_params: Optional[Dict[str, Any]] = None,
                             sorts: Optional[list] = None) -> Dict[str, Any]:
    """
    데이터베이스의 모든 결과를 가져옵니다 (페이지네이션 처리)
    """
    has_more = True
    start_cursor = None
    all_results = []

    while has_more:
        response = await self.query_database(
            database_id=database_id,
            filter_params=filter_params,
            sorts=sorts,
            start_cursor=start_cursor
        )

        all_results.extend(response.get("results", []))

        # 다음 페이지 확인
        has_more = response.get("has_more", False)
        if has_more:
            start_cursor = response.get("next_cursor")
        else:
            break

    # 원본 응답 형식 유지하면서 모든 결과 반환
    return {
        "object": "list",
        "results": all_results,
        "has_more": False,
        "next_cursor": None
    }
