from datetime import datetime, timedelta, timezone
import sqlite3
from jose import JWTError, jwt # type: ignore # ! change in github
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer
import bcrypt
import re

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
path = "HMCTS\\Backend"

# password needs to be 10 characters+, contain at least one uppercase letter, one number, and one special character
def hash_password(password:str) -> str:
    valid_password = r"^(?=.*[A-Z]+)(?=.*[0-9]+)(?=.*[^a-zA-Z0-9]+).{10,}$"
    password_match = re.search(valid_password, password)
    if password_match is None:
        raise HTTPException(status_code=400, detail="Password must be at least 10 characters long and contain at least one uppercase letter, one number, and one special character")
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode("utf-8")

def check_password(password:str, hashed:str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def authenticate_user(username: str, password: str):
    conn = sqlite3.connect(path + "\\users.db", check_same_thread=False) 
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if not user or not check_password(password, user[2]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    return{"id": user[0], "username": user[1], "password": user[2], "role": user[3]}

def create_access_token(user: dict):
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "username": user["username"],
        "role": user["role"],
        "id": user["id"],  
        "exp": expire
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str = Depends(oauth2_scheme)):
    try:    
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        id = payload.get("id")
        role = payload.get("role")
        if not username or not role:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return {"id": id, "username": username, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
def require_role(required_role: str):
    def role_dependency(user: dict = Depends(verify_token)):
        if user["role"] != required_role:
            raise HTTPException(status_code=403, detail="Access forbidden")
        return user
    return role_dependency