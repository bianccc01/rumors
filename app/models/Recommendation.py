from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Recommendation(BaseModel):
    item_id: str
    score: float
    pred_score: float
    is_known: bool
    timestamp: datetime
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: int = Field(default=1)
    deleted_at: Optional[datetime] = None
