from sqlmodel import create_engine, Session, SQLModel
from app.models import PatientAssessment
from fastapi import Depends
from typing import Annotated

connect_args = {"check_same_thread": False}
engine = create_engine("sqlite:///triage.db", connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session

def create_tables():
    SQLModel.metadata.create_all(engine)

SessionDep = Annotated[Session, Depends(get_session)]
