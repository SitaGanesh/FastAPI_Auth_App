from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal,engine
import models
from models import User
import bcrypt
import httpx
from dotenv import load_dotenv
import os

GOOGLE_CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI=os.getenv("GOOGLE_REDIRECT_URI")

#Automatically create the database tables if they dont exist yet
models.Base.metadata.create_all(bind=engine)

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class RegisterUser(BaseModel):
    username:str
    email:str
    password:str

class LoginUser(BaseModel):
    email:str
    password:str

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
def register(user:RegisterUser, db:Session=Depends(get_db)):
        #checking user have already email id taken
        existing=db.query(User).filter(User.email==user.email).first()

        if existing:
            raise HTTPException(status_code=400, detail={"message":"Email already exist"})
        #creating plain text password for security
        hashed=bcrypt.hashpw(
            user.password.encode('utf-8'),
            bcrypt.gensalt()
        )

        #create a new user database object
        new_user=User(
            username=user.username,
            email=user.email,
            password_hash=hashed.decode('utf-8')

        )
        db.add(new_user)
        db.commit()
        return {"message":"User registration successful"}
    


@app.post("/login")
def login(user: LoginUser, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    
    # 1. User doesn't exist
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid Credentials")
        
    valid = bcrypt.checkpw(
        user.password.encode('utf-8'),
        db_user.password_hash.encode('utf-8')
    )
    
    # 2. Login Successful
    if valid:
        return {
            "success": True,
            "username": db_user.username
        }
        
    # 3. Password doesn't match
    raise HTTPException(status_code=400, detail="Invalid Credentials")

class GoogleAuthRequest(BaseModel):
    code: str


@app.post("/auth/google")
async def google_auth(data: GoogleAuthRequest, db:Session=Depends(get_db)):
    async with httpx.AsyncClient() as client:
        token_response=await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code":data.code,
                "client_id":GOOGLE_CLIENT_ID,
                "client_secret":GOOGLE_CLIENT_SECRET,
                "redirect_uri":GOOGLE_REDIRECT_URI,
                "grant_type":"authorization_code",
            },
        )
        token_data=token_response.json()
        if "error" in token_data:
            raise HTTPException(status_code=400, detail=token_data.get("error_description","Failed to verify"))
        access_token=token_data.get("access_token")
        user_info_response=await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization":f"Bearer {access_token}"}

        )
        user_info=user_info_response.json()

    email=user_info.get("email")
    name=user_info.get("name")

    if not email:
        raise HTTPException(status_code=400,detail="Could not retrieve email from Google")
    
    db_user=db.query(User).filter(User.email==email).first()
    if not db_user:
        db_user=User(
            username=name,
            email=email,
            password_hash=None,
            
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    return {
        "success":True,
        "username":db_user.username,
        "email":db_user.email
    }