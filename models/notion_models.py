from typing import List
from pydantic import BaseModel

class NotionPage(BaseModel):
    id: str
    title: str
    url: str
    created_time: str
    last_edited_time: str

class NotionPagesResponse(BaseModel):
    pages: List[NotionPage]
    total_count: int