import os
import ssl
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Read from environment
raw_url = os.getenv("DATABASE_URL") or os.getenv("PRODUCTION_DATABASE_URL")

connect_args = {}

if not raw_url:
    # Local development string
    DATABASE_URL = os.getenv("LOCAL_DATABASE_URL", "mysql+pymysql://root:captainamerica@localhost/auth")
else:
    # Safely parse the incoming URL object
    url = make_url(raw_url)

    # Force the pymysql driver dialect interface wrapper
    if url.drivername == "mysql":
        url = url.set(drivername="mysql+pymysql")

    # Extract query parameters to clean them up
    cleaned_query = dict(url.query)
    
    # Safely pop out any conflicting ssl parameter variations
    ssl_mode = (
        cleaned_query.pop("ssl_mode", None) or 
        cleaned_query.pop("sslmode", None) or 
        cleaned_query.pop("ssl-mode", None)
    )

    # Rebuild the final clean database URL string
    url = url.set(query=cleaned_query)
    DATABASE_URL = str(url)

    # If an SSL constraint was requested by Aiven, apply the custom SSL context safely
    if ssl_mode:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Inject the context cleanly for PyMySQL
        connect_args["ssl"] = ssl_context

# Pass connect_args directly into the initialization pipeline
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()