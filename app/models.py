from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Optional

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

class PatientAssessment(BaseModel):
    id: Optional[int] = None
    notes: str
    esi_level: int
    diagnosis: str
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