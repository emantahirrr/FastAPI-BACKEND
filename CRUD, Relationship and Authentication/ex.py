#exercise Q
#1. Full CRUD. Give your Item resource all of POST/GET/GET-by-id/PATCH/DELETE with correct status codes.
#2. Relationship. Add a Category table and link items to it; list all items in one category.
#3. Register & login. Add POST /register (hash the password) and POST /token (verify, return a JWT).
#4. Protect. Require current_user on item-mutating endpoints; confirm a missing token returns 401.


from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import SQLModel, Field, Relationship, Session, create_engine, select
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

# --- Config ---
SECRET = "change-me-in-env"
ALGO = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2 = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()
engine = create_engine("sqlite:///db.db")

# --- Models ---
class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    items: list["Item"] = Relationship(back_populates="category")

class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    category_id: int | None = Field(default=None, foreign_key="category.id")
    category: Category | None = Relationship(back_populates="items")

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    password_hash: str

# --- DB setup ---
def get_session():
    with Session(engine) as session:
        yield session

SQLModel.metadata.create_all(engine)

# --- Helpers ---
def hash_pw(p: str) -> str: return pwd_context.hash(p)
def verify_pw(p: str, h: str) -> bool: return pwd_context.verify(p, h)

def make_token(sub: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(hours=12)
    return jwt.encode({"sub": sub, "exp": exp}, SECRET, algorithm=ALGO)

def current_user(token: str = Depends(oauth2), session: Session = Depends(get_session)) -> User:
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
        username = payload.get("sub")
        user = session.exec(select(User).where(User.username == username)).first()
        if not user:
            raise HTTPException(401, "Invalid user")
        return user
    except JWTError:
        raise HTTPException(401, "Invalid or expired token")

# --- Auth Endpoints ---
@app.post("/register")
def register(username: str, password: str, session: Session = Depends(get_session)):
    if session.exec(select(User).where(User.username == username)).first():
        raise HTTPException(400, "Username taken")
    user = User(username=username, password_hash=hash_pw(password))
    session.add(user); session.commit()
    return {"msg": "Registered"}

@app.post("/token")
def login(form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == form.username)).first()
    if not user or not verify_pw(form.password, user.password_hash):
        raise HTTPException(401, "Bad credentials")
    return {"access_token": make_token(user.username), "token_type": "bearer"}

# --- CRUD Endpoints for Items ---
@app.post("/items", response_model=Item, status_code=201)
def create_item(item: Item, session: Session = Depends(get_session), user: User = Depends(current_user)):
    session.add(item); session.commit(); session.refresh(item)
    return item

@app.get("/items", response_model=list[Item])
def list_items(session: Session = Depends(get_session)):
    return session.exec(select(Item)).all()

@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if not item: raise HTTPException(404, "Item not found")
    return item

@app.patch("/items/{item_id}", response_model=Item)
def update_item(item_id: int, data: dict, session: Session = Depends(get_session), user: User = Depends(current_user)):
    item = session.get(Item, item_id)
    if not item: raise HTTPException(404, "Item not found")
    for k, v in data.items(): setattr(item, k, v)
    session.add(item); session.commit(); session.refresh(item)
    return item

@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, session: Session = Depends(get_session), user: User = Depends(current_user)):
    item = session.get(Item, item_id)
    if not item: raise HTTPException(404, "Item not found")
    session.delete(item); session.commit()
    return None

# --- Relationship Query ---
@app.get("/categories/{cat_id}/items", response_model=list[Item])
def items_in_category(cat_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Item).where(Item.category_id == cat_id)).all()
