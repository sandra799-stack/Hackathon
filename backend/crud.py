from requests import Session
from applicationDb import SessionLocal
from models import Promotion
from sqlalchemy import text

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