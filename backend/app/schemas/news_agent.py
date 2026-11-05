from datetime import datetime

from pydantic import BaseModel, HttpUrl


class NewsCollectionResponse(BaseModel):
    source: HttpUrl
    retrieved_at: datetime
    listed: int
    imported: int
    duplicates: int
    failed: int
