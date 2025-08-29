from typing import Optional
from pydantic import BaseModel
class PromotionWithStatus(BaseModel):
    id: int
    description: str
    promotion_name: str
    icon: Optional[str] = None
    is_active: bool
    class Config:
        orm_mode = True