from fastapi import APIRouter
from app.models import PatientAssessment
from app.engine import SupabaseDep
from app.repository.AssessmentRepository import AssessmentRepository

AssessmentRouter = APIRouter(
    prefix="/assessments",
    tags=["assessments"],
    redirect_slashes=True
)

@AssessmentRouter.post("", response_model=PatientAssessment)
def create_assessment(assessment: PatientAssessment, session: SupabaseDep):
    """Create a new patient assessment"""
    assessment_repository = AssessmentRepository(session)
    return assessment_repository.create(
        notes=assessment.notes,
        esi_level=assessment.esi_level,
        diagnosis=assessment.diagnosis
    )

@AssessmentRouter.get("", response_model=list[PatientAssessment])
def get_assessments(session: SupabaseDep):
    """Get all patient assessments"""
    assessment_repository = AssessmentRepository(session)
    return assessment_repository.get_all()

@AssessmentRouter.delete("/{assessment_id}")
def delete_assessment(assessment_id: int, session: SupabaseDep):
    """Delete a patient assessment by ID"""
    assessment_repository = AssessmentRepository(session)
    assessment_repository.delete_by_id(assessment_id)
    return {"message": "Assessment deleted successfully"}