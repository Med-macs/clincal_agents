from fastapi import APIRouter
from app.models import PatientAssessment
from app.engine import SessionDep
from app.repository.AssessmentRepository import AssessmentRepository

AssessmentRouter = APIRouter(prefix="/assessments", redirect_slashes=True)

@AssessmentRouter.post("")
def create_assessment(assessment: PatientAssessment, session: SessionDep):
    assessment_repository = AssessmentRepository(session)
    assessment_repository.create(assessment.notes, assessment.esi_level, assessment.diagnosis)
    return assessment

@AssessmentRouter.get("")
def get_assessments(session: SessionDep):
    assessment_repository = AssessmentRepository(session)
    return assessment_repository.get_all()

@AssessmentRouter.delete("")
def delete_all_assessments(session: SessionDep):
    assessment_repository = AssessmentRepository(session)
    assessment_repository.delete_all()
    return {"message": "All assessments deleted successfully"}