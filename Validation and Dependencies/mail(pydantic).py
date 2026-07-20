#steps
#1. Define UserCreate with constraints via Field.
#2. Define UserPublic — the only fields a client should see.
#3. Wire them with response_model so output is filtered automatically.







from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field
app= FastAPI()
class UserCreate(BaseModel):
    email: EmailStr
    username:str = Field(min_length=3, max_length=8)
    password: str = Field(min_length=8)
    age: int| None = Field(deafult=None, ge=13, le=120)
class UserPublic(BaseModel):
    id: int
    username: str
@app.post("/user", response_model=UserPublic, status_code=201)
def create_user(payload:UserCreate):
    return{"id":1, "username":payload.username, "email": payload.email, "password":"leaked?" }