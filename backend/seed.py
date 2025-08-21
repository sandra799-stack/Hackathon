from applicationDb import Base, engine
from crud import clear_promotions, create_promotions_bulk

def run_seed():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    # Clear old data
    clear_promotions()

    # Insert fresh data
    create_promotions_bulk([
            {"description": "Happy Hour", "promotion_name": "Happy Hour"},
            {"description": "Birthday", "promotion_name": "Birthday"},
            {"description": "Social media posts", "promotion_name": "Social media posts"},
            {"description": "Know your coustomer", "promotion_name": "Know your coustomer"},
            {"description": "Recommend Items", "promotion_name": "Recommend Items"},
            {"description": "PromoCode depnding on the weather", "promotion_name": "PromoCode depnding on the weather"}
    ])
    print("✅ Promotions cleared and re-seeded")

if __name__ == "__main__":
    run_seed()
