# triage_ai_assistant/app/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from agents.triageagent import run_triage_workflow
from agents.nursebot import run_chat

app = FastAPI(title="AI Triage API")

class TriageRequest(BaseModel):
    note: str

class TriageResponse(BaseModel):
    esi: str
    diagnosis: str
    iterations: int

@app.get("/")
def root():
    return {"message": "Triage API is running"}

@app.post("/triage", response_model=TriageResponse)
def triage_endpoint(data: TriageRequest):
    result = run_triage_workflow(data.note)
    return TriageResponse(**result)

@app.post("/chat-to-triage", response_model=TriageResponse)
def chat_to_triage():
    config = {"recursion_limit": 50}
    state = run_chat(config)
    combined_note = "\n".join(state.get("notes", []))
    print("Notes Collected: ", combined_note)
    result = run_triage_workflow(combined_note)
    return TriageResponse(**result)
