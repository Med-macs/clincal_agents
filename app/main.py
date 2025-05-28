from fastapi import FastAPI
from agents.triageagent import run_triage_workflow
from agents.nursebot import NURSEBOT_SYSINT, WELCOME_MSG, llm_with_tools
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.engine import SupabaseDep
from app.routers.AssessmentRouter import AssessmentRouter
from app.routers.TriageRouter import TriageRouter
from app.routers.UserRouter import UserRouter
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Triage API",
    ignore_trailing_slash=True
)

# Configure CORS for Cloud Run
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Routers
app.include_router(AssessmentRouter, prefix="/api/v1")
app.include_router(TriageRouter, prefix="/api/v1")
app.include_router(UserRouter, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "message": "Triage API is running",
        "docs_url": "/docs",
        "version": "1.0.0"
    }



