import os
import certifi
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Read from environment
raw_url = os.getenv("DATABASE_URL") or os.getenv("PRODUCTION_DATABASE_URL")

if not raw_url:
    # Local development string
    DATABASE_URL = os.getenv("LOCAL_DATABASE_URL", "mysql+pymysql://root:captainamerica@localhost/auth")
else:
    # Normalize URLs from managed MySQL providers so SQLAlchemy/PyMySQL
    # does not receive unsupported ssl_mode keyword arguments.
    url = make_url(raw_url)
    connect_args = {}

    if url.drivername == "mysql":
        url = url.set(drivername="mysql+pymysql")

    cleaned_query = dict(url.query)
    ssl_mode = cleaned_query.pop("ssl_mode", None) or cleaned_query.pop("sslmode", None) or cleaned_query.pop("ssl-mode", None)

    DATABASE_URL = str(url.set(query=cleaned_query))

    if ssl_mode:
        connect_args["ssl"] = {"ca": certifi.where()}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()