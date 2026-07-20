#1. New table. Add an Item table (id, name indexed, price float). Create and list items via endpoints and confirm rows survive a restart.
#2. Read one. Add GET /items/{id} using session.get(Item, id); return 404 with HTTPException when missing.
#3. Transaction proof. In a test endpoint, add a row then raise before commit; confirm the row is absent afterward.
#4. Migration. Initialise Alembic, autogenerate a migration for your tables, and apply it. Inspect the generated script.


from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Session, select, Field, create_engine
app= FastAPI()
class Item(SQLModel, table=True):
    id: int| None =Field(default=None, primary_key=True)
    name: str = Field(index=True)
    price: float
engine= create_engine("sqlite:///./dev.db")
SQLModel.metadata.create_all(engine)
def get_session():
    with Session(engine) as session:
        yield session
@app.post("/item", response_model=Item, status_code=201)
def create_item(item:Item, session: Session= Depends(get_session)):
    session.add_all(item)
    session.commit()
    session.refresh(itme)
    return item
@app.get("/item", response_model=list[Item])
def list_item(session: Session= Depends(get_session)):
    return session.exec(select(Item)).all()
@app.get("/items/{id}", response_model=Item)
def read_item(id: int, session: Session = Depends(get_session)):
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
@app.post("/items/test")
def test_transaction(item: Item, session: Session = Depends(get_session)):
    session.add(item)
    # simulate an error before commit
    raise RuntimeError("Simulated failure")
    session.commit()
    return item
