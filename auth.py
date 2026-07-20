#Worked Example — Hash a password, issue and verify a token
#Step 1. Hash and verify passwords with bcrypt via passlib.
#Step 2. Issue a signed, expiring JWT on login.
#Step 3. Write a current_user dependency that decodes the token or returns 401.



from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError
app=FastAPI()
pwd = CryptContext(schemes=["bcrypt"])
SECRET = "change-me-in-env"; ALGO = "HS256"
oauth2 = OAuth2PasswordBearer(tokenUrl="token")
 
def hash_pw(p: str) -> str: return pwd.hash(p)
def verify_pw(p: str, h: str) -> bool: return pwd.verify(p, h)
 
def make_token(sub: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(hours=12)
    return jwt.encode({"sub": sub, "exp": exp}, SECRET, algorithm=ALGO)
 
def current_user(token: str = Depends(oauth2)) -> str:
    try:
        return jwt.decode(token, SECRET, algorithms=[ALGO])["sub"]
    except JWTError:
        raise HTTPException(401, "Invalid or expired token")

@app.get("/me")
def me(user: str = Depends(current_user)):
    return {"user": user}