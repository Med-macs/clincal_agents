from app.models import PatientAssessment
from datetime import datetime, UTC
from app.engine import SupabaseDep
from typing import Optional, List

class AssessmentRepository:
    def __init__(self, session: SupabaseDep):
        self.session = session

    def create(self, notes: str, esi_level: int, diagnosis: str) -> PatientAssessment:
        assessment = PatientAssessment(
            notes=notes,
            esi_level=esi_level,
            diagnosis=diagnosis
        )
        response = self.session.table("assessments").insert(assessment.model_dump()).execute()
        return PatientAssessment(**response.data[0])

    def get_all(self) -> List[PatientAssessment]:
        response = self.session.table("assessments").select("*").execute()
        return [PatientAssessment(**item) for item in response.data]

    def get_by_id(self, assessment_id: int) -> Optional[PatientAssessment]:
        response = self.session.table("assessments").select("*").eq("id", assessment_id).execute()
        return PatientAssessment(**response.data[0]) if response.data else None

    def delete_by_id(self, assessment_id: int) -> bool:
        assessment = self.get_by_id(assessment_id)
        if assessment:
            self.session.table("assessments").delete().eq("id", assessment_id).execute()
            return True
        return False
