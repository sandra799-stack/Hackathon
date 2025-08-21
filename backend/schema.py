from pydantic import BaseModel
class PromotionWithStatus(BaseModel):
    id: int
    description: str
    promotion_name: str
    is_active: bool

    class Config:
        orm_mode = True