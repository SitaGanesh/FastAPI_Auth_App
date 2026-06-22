from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Local fallback
    DATABASE_URL = os.getenv("LOCAL_DATABASE_URL", "mysql+pymysql://root:captainamerica@localhost/auth")
else:
    # 1. Force the use of the pymysql dialect driver wrapper
    if DATABASE_URL.startswith("mysql://"):
        DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)
    
    # 2. Fix the Aiven query parameter conflict ('ssl-mode' -> 'ssl_mode')
    if "ssl-mode=" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("ssl-mode=", "ssl_mode=")

        
#this manages actual database engine- core pipeline to mysql
engine=create_engine(DATABASE_URL)

# sessionlocal instances will be the actual interface to talk to the database
SessionLocal=sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base=declarative_base()
