from pydantic import BaseModel
from sqlmodel import SQLModel, Field
from datetime import datetime, UTC
from typing import List, Dict, Optional
from sqlalchemy import DateTime

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]]
    patient_name: str
    patient_email: str

class ChatResponse(BaseModel):
    response: str
    finished: bool
    notes: Optional[List[str]] = None

class TriageRequest(BaseModel):
    note: str

class TriageResponse(BaseModel):
    esi: str
    diagnosis: str
    iterations: int

class PatientAssessment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    notes: str
    esi_level: int
    diagnosis: str
    created_at: datetime = Field(
        sa_type=DateTime(),
        default_factory=lambda: datetime.now(UTC).replace(tzinfo=None)
    )