#Worked Example — Update + delete with a relationship
#Step 1. Add a team_id foreign key and a Relationship.
#Step 2. PATCH loads the row, applies only provided fields, re-commits.
#Step 3. DELETE removes the row, returning 204 with no body.


from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Session, select, Field, create_engine, Relationship
app= FastAPI()
class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    heroes: list["Hero"] = Relationship(back_populates="team")
 
class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    team_id: int | None = Field(default=None, foreign_key="team.id")
    team: Team | None = Relationship(back_populates="heroes")
engine= create_engine("sqlite:///./crud.db")
SQLModel.metadata.create_all(engine)
def get_session():
    with Session(engine) as session:
        yield session
@app.patch("/heroes/{hero_id}", response_model=Hero)
def update_hero(hero_id: int, data: dict, session: Session = Depends(get_session)):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(404, "Hero not found")
    for k, v in data.items():
        setattr(hero, k, v)             
    session.add(hero); 
    session.commit(); 
    session.refresh(hero)
    return hero
 
@app.delete("/heroes/{hero_id}", status_code=204)
def delete_hero(hero_id: int, session: Session = Depends(get_session)):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(404, "Hero not found")
    session.delete(hero); 
    session.commit()