from sqlalchemy import func
from requests import Session
from models import * 

def get_promotions(db: Session , merchant_id: str):
    sql = text("""
        select Id,description, promotion_name,
	    case when ap.promotion_id is null then False else True end AS is_active
        From public.promotions p
        Left join (
	       select promotion_id
	       from public.active_promotions 
	       WHERE merchant_id = :merchant_id )  ap on  p.id = ap.promotion_id
    """)
    result = db.execute(sql, {"merchant_id": merchant_id})
    return result.fetchall()

def clear_promotions(db: Session):
    """Delete all promotions from the table."""
    db.query(Promotion).delete()
    db.commit()
    db.close()

def create_promotions_bulk(db: Session, promotions_data: list[dict]):
    """Insert multiple promotions at once."""
    promotions = [Promotion(description = data['description'], promotion_name = data['promotion_name']) for data in promotions_data]
    db.add_all(promotions) # efficient bulk insert
    db.commit()
    db.close()

def insert_active_promotion(db: Session, merchant_id: str, promotion_name: str):
    promo = db.query(Promotion).filter(func.lower(Promotion.promotion_name) == promotion_name.lower()).first()
    if not promo:
        raise ValueError(f"Promotion with name '{promotion_name}' not found")
    active_promo = ActivePromotion(merchant_id = merchant_id, promotion_id = promo.id)
    db.add(active_promo)
    db.commit()
    db.refresh(active_promo)
    return active_promo

def delete_active_promotion(db: Session, merchant_id: str, promotion_name: str):
    promo = db.query(Promotion).filter(func.lower(Promotion.promotion_name) == promotion_name.lower()).first()
    if not promo:
        raise ValueError(f"Promotion with name '{promotion_name}' not found")
    active_promo = (
        db.query(ActivePromotion).filter(ActivePromotion.merchant_id == merchant_id,ActivePromotion.promotion_id == promo.id).first()
    )
    if not active_promo:
        raise ValueError(f"Active promotion '{promotion_name}' not found for merchant {merchant_id}")
    db.delete(active_promo)
    db.commit()
    return