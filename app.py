from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional

app = FastAPI()

# DB setup
sqlite_file_name = "leads.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)  # echo=True prints SQL (helpful for debug)

class Lead(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    last_name: str
    company: str
    status: str = "New"

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/leads", response_model=Lead)
def create_lead(lead: Lead):
    with Session(engine) as session:
        session.add(lead)
        session.commit()
        session.refresh(lead)
        return lead

@app.get("/leads")
def get_leads():
    with Session(engine) as session:
        leads = session.exec(select(Lead)).all()
        return leads

@app.get("/leads/{lead_id}", response_model=Lead)
def get_lead(lead_id: int):
    with Session(engine) as session:
        lead = session.get(Lead, lead_id)
        if not lead:
            raise HTTPException(404, "Lead not found")
        return lead

@app.put("/leads/{lead_id}", response_model=Lead)
def update_lead(lead_id: int, updated: Lead):
    with Session(engine) as session:
        lead = session.get(Lead, lead_id)
        if not lead:
            raise HTTPException(404, "Lead not found")
        lead.last_name = updated.last_name
        lead.company = updated.company
        lead.status = updated.status
        session.add(lead)
        session.commit()
        session.refresh(lead)
        return lead

@app.delete("/leads/{lead_id}")
def delete_lead(lead_id: int):
    with Session(engine) as session:
        lead = session.get(Lead, lead_id)
        if not lead:
            raise HTTPException(404, "Lead not found")
        session.delete(lead)
        session.commit()
        return {"detail": "deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)