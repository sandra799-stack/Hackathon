from app_db import Base, engine, SessionLocal
from crud import clear_promotions, create_promotions_bulk

def run_seed(db):
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    # Clear old data
    clear_promotions(db)

    # Insert fresh data
    create_promotions_bulk(db, [
            {"description": "Happy Hour", "promotion_name": "Happy Hour", "icon":"AnimatedClock"},
            {"description": "Birthday", "promotion_name": "Birthday" , "icon":"AnimatedCake"},
            {"description": "Social media posts", "promotion_name": "Social media posts" ,"icon":"AnimatedShare2"},
            {"description": "Know your coustomer", "promotion_name": "Know your coustomer" ,"icon":"AnimatedUsers"},
            {"description": "Recommend Items", "promotion_name": "Recommend Items" ,"icon":"AnimatedStar"},
            {"description": "PromoCode depnding on the weather", "promotion_name": "PromoCode depnding on the weather","icon":"AnimatedCake"}
    ])
    print("✅ Promotions cleared and re-seeded")

if __name__ == "__main__":
    db = SessionLocal()
    run_seed(db)
