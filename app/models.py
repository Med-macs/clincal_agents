from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]]
    patient_id: int

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

class PatientAssessment(BaseModel):
    id: Optional[int] = None
    notes: str
    esi_level: int
    diagnosis: str
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        # Remove None values to let database defaults handle them
        return {k: v for k, v in data.items() if v is not None and k != 'id'}

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class UserType(str, Enum):
    PATIENT = "patient"
    STAFF = "staff"

class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: EmailStr
    age: int
    gender: str
    user_type: UserType
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        return {k: v for k, v in data.items() if v is not None and k != 'id'}

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class UserLogin(BaseModel):
    name: str
    email: EmailStr
    age: int
    gender: str
    user_type: UserType