from sqlalchemy import create_engine
from app.db.database import DATABASE_URL, engine
from app.models.database_models import Base

def init_database():
    print(f"Initializing database at {DATABASE_URL}...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully.")

if __name__ == "__main__":
    init_database()
