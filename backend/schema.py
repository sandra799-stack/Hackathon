from pydantic import BaseModel
from datetime import datetime

class PromotionBase(BaseModel):
    description: str
    promotion_name: str

class PromotionCreate(PromotionBase):
    pass

class PromotionResponse(PromotionBase):
    id: int
    class Config:
        orm_mode = True


class ActivePromotionBase(BaseModel):
    merchant_id: str

class ActivePromotionCreate(ActivePromotionBase):
    promotion_id: int

class ActivePromotionResponse(ActivePromotionBase):
    id: int
    applied_at: datetime
    promotion: PromotionResponse

    class Config:
        orm_mode = True
