from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class ReviewEntry(BaseModel):
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: Optional[str] = None
    professor_id: str
    course_number: str
    department: str
    content: str
    quality: int
    ease: int
    grade: Optional[str] = None
    tags: Optional[list] = None
    take_again: bool
    is_user_anonymous: bool