#Example — Define a table, persist a row, read it back
#Step 1. Declare Hero as a SQLModel table with a primary key and an index.
#Step 2. Create an engine and a get_session dependency (open fi yield fi auto-close).
#Step 3. Write create and list endpoints; commit() to persist, refresh() to load the DB-generated id.


from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Session, select, Field, create_engine
app= FastAPI()
class Hero(SQLModel, table=True):
    id: int| None =Field(default=None, primary_key=True)
    name: str = Field(index=True)
    power: str
engine= create_engine("sqlite:///./dev.db")
SQLModel.metadata.create_all(engine)
def get_session():
    with Session(engine) as session:
        yield session
@app.post("/heroes", response_model=Hero, status_code=201)
def create_hero(hero:Hero, session: Session= Depends(get_session)):
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero
@app.get("/heroes", response_model=list[Hero])
def list_heroes(session: Session= Depends(get_session)):
    return session.exec(select(Hero)).all()
