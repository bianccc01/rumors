from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models import Rating
from app.models import Recommendation


class User(BaseModel):
    email: Optional[str] = None
    age: Optional[str] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    education: Optional[str] = None
    job: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    language: Optional[str] = None
    ratings: List[Rating] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: int = Field(default=1)
    deleted_at: Optional[datetime] = None
