from app_db import Base, engine, SessionLocal
from crud import clear_promotions, create_promotions_bulk

def run_seed(db):
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    # Clear old data
    clear_promotions(db)

    # Insert fresh data
    create_promotions_bulk(db, [
            {"description": "Boost sales with limited-time discounts during happy hours.", "promotion_name": "Happy Hour", "icon":"AnimatedClock"},
            {"description": "Celebrate your customers’ birthdays with special offers they’ll love.", "promotion_name": "Birthday" , "icon":"AnimatedCake"},
            {"description": "Promote your store with eye-catching posts on social media.", "promotion_name": "Social Media Posts" ,"icon":"AnimatedShare2"},
            {"description": "Send customers a quick form to learn more about them and personalize your offers.", "promotion_name": "Know Your Customer" ,"icon":"AnimatedUsers"},
            {"description": "Recommend items based on customer order history", "promotion_name": "Personalized Recommendation" ,"icon":"AnimatedStar"},
            {"description": "Share promo codes based on the weather to boost engagement.","promotion_name": "Weather Recommendation","icon": "AnimatedSunCloud"}
    ])
    print("✅ Promotions cleared and re-seeded")

if __name__ == "__main__":
    db = SessionLocal()
    run_seed(db)
