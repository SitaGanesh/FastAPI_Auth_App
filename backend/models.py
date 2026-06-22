from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    ##what to name actual table name in db
    __tablename__="users"

    id=Column(Integer, primary_key=True, index=True)
    username=Column(String(200))
    email=Column(String(255), unique=True, index=True)
    #nullable true because, OAuth user dont require password hash
    password_hash=Column(String(255),nullable=True)