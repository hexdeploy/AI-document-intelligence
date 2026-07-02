import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Fetch the Database URL from Render environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Set up the engine and session maker (Removed the incorrect create_session import)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Create the base class for database tables
Base = declarative_base()

# 4. Dependency to get DB session in endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()