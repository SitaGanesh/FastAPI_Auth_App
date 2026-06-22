import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Read from environment
raw_url = os.getenv("DATABASE_URL")

if not raw_url:
    # Local development string
    DATABASE_URL = os.getenv("LOCAL_DATABASE_URL", "mysql+pymysql://root:captainamerica@localhost/auth")
else:
    # Double check protocol configuration
    if raw_url.startswith("mysql://"):
        raw_url = raw_url.replace("mysql://", "mysql+pymysql://", 1)
    
    # Force replace hyphen if it's still hanging around
    if "ssl-mode=" in raw_url:
        raw_url = raw_url.replace("ssl-mode=", "ssl_mode=")
        
    DATABASE_URL = raw_url

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()