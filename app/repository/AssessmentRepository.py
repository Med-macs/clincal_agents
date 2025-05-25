from sqlmodel import Session, select
from app.models import PatientAssessment
from datetime import datetime, UTC

class AssessmentRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, notes: str, esi_level: int, diagnosis: str) -> PatientAssessment:
        assessment = PatientAssessment(
            notes=notes,
            esi_level=esi_level,
            diagnosis=diagnosis,
            created_at=datetime.now(UTC).replace(tzinfo=None)
        )
        self.session.add(assessment)
        self.session.commit()
        self.session.refresh(assessment)
        return assessment

    def get_all(self) -> list[PatientAssessment]:
        return self.session.exec(select(PatientAssessment)).all()

    def get_by_id(self, assessment_id: int) -> PatientAssessment | None:
        return self.session.get(PatientAssessment, assessment_id)

    def delete_all(self) -> None:
        self.session.exec(select(PatientAssessment)).delete()
        self.session.commit()

    def delete_by_id(self, assessment_id: int) -> bool:
        assessment = self.get_by_id(assessment_id)
        if assessment:
            self.session.delete(assessment)
            self.session.commit()
            return True
        return False
