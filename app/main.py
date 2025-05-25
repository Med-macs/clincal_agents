from fastapi import FastAPI, Depends
from agents.triageagent import run_triage_workflow
from agents.nursebot import NURSEBOT_SYSINT, WELCOME_MSG, llm_with_tools
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import logging
from app.engine import SessionDep, create_tables
from contextlib import asynccontextmanager
from app.routers.AssessmentRouter import AssessmentRouter
from app.routers.TriageRouter import TriageRouter
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="AI Triage API",
    lifespan=lifespan,
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

@app.get("/")
def root():
    return {
        "message": "Triage API is running",
        "docs_url": "/docs",
        "version": "1.0.0"
    }



