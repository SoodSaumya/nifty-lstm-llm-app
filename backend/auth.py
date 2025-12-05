from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from jose import jwt
from datetime import datetime, timedelta
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import hashlib

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Auth"])

# MongoDB setup
client = MongoClient(os.getenv("MONGO_URI"))
db = client["stockPredictionDB"]
users = db["users"]

# JWT setup
JWT_SECRET = os.getenv("JWT_SECRET", "supersecret123")
JWT_EXPIRE_MIN = 1440  # 24 hours


# ============================
#   MODELS
# ============================
class SignupModel(BaseModel):
    name: str
    email: str
    password: str


class LoginModel(BaseModel):
    email: str
    password: str


# ============================
#   JWT FUNCTION
# ============================
def create_jwt(data: dict):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MIN)
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


# ============================
#   SIGNUP
# ============================
@router.post("/signup")
def signup(user: SignupModel):

    # Check duplicate email
    if users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists")

    # Hash password using SHA256
    hashed_pw = hashlib.sha256(user.password.encode()).hexdigest()

    # Insert user in DB
    users.insert_one({
        "name": user.name,
        "email": user.email,
        "password": hashed_pw
    })

    return {"message": "User created successfully!"}


# ============================
#   LOGIN
# ============================
@router.post("/login")
def login(data: LoginModel):
    user = users.find_one({"email": data.email})

    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # Hash user input and compare
    hashed_input = hashlib.sha256(data.password.encode()).hexdigest()

    if hashed_input != user["password"]:
        raise HTTPException(status_code=400, detail="Incorrect password")

    # Create JWT token
    token = create_jwt({
        "email": user["email"],
        "name": user["name"]
    })

    return {
        "message": "Login successful",
        "token": token,
        "name": user["name"],
        "email": user["email"]
    }
