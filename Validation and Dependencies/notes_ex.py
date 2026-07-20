#steps
#1. Constrained model. Build NoteCreate with title (3–80 chars) and body (max 5000). Reject blanks;confirm the 422 message names the field.
#2. Hide a field. Create NotePublic that omits an internal secret_token field and prove it never appears in the response.
#3. Reuse a dependency. Add the pagination dependency to two endpoints and verify limit=999 is clamped to 100.
#4. Validator. Add a Pydantic field validator that lowercases and strips the email before storage.


from fastapi import FastAPI, Query, Depends
from pydantic import BaseModel, Field, EmailStr, field_validator

app = FastAPI()

class NoteCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=80)
    body: str = Field(..., min_length=1, max_length=5000)

class NotePublic(BaseModel):
    id: int
    title: str
    body: str

@app.post("/notes", response_model=NotePublic)
def create_note(note: NoteCreate):
    return {
        "id": 1,
        "title": note.title,
        "body": note.body,
        "secret_token": "secret"   
    }


def pagination( skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)):
    return {
        "skip": skip,"limit": limit }

@app.get("/notes")
def list_notes(p=Depends(pagination)):
    return {"pagination": p}

@app.get("/users")
def list_users(p=Depends(pagination)):
    return {"pagination": p}

class User(BaseModel):
    email: EmailStr
    @field_validator("email")
    @classmethod
    def normalize_email(cls, v):
        return v.strip().lower()