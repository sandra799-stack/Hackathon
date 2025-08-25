from app_db import Base, engine, SessionLocal
from crud import clear_promotions, create_promotions_bulk

def run_seed(db):
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    # Clear old data
    clear_promotions(db)

    # Insert fresh data
    create_promotions_bulk(db, [
            {"description": "Happy Hour", "promotion_name": "Happy Hour"},
            {"description": "Birthday", "promotion_name": "Birthday"},
            {"description": "Social media posts", "promotion_name": "Social media posts"},
            {"description": "Know your coustomer", "promotion_name": "Know your coustomer"},
            {"description": "Recommend Items", "promotion_name": "Recommend Items"},
            {"description": "PromoCode depnding on the weather", "promotion_name": "PromoCode depnding on the weather"}
    ])
    print("✅ Promotions cleared and re-seeded")

if __name__ == "__main__":
    db = SessionLocal()
    run_seed(db)
