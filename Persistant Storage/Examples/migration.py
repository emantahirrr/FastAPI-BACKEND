# Example — Initialise and apply a migration
#Step 1. Initialise Alembic and point it at your database URL and SQLModel.metadata.
#Step 2. Autogenerate a migration from your models.
#Step 3. Apply it with upgrade; learn the rollback command.
#run in terminal
# ->alembic init migrations
# in migrations/env.py:  target_metadata = SQLModel.metadata
# in alembic.ini:        sqlalchemy.url = sqlite:///./dev.db
 
# ->alembic revision --autogenerate -m "create hero table"
# ->alembic upgrade head        # apply the latest migration
# ->alembic downgrade -1        # roll back one step if needed



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