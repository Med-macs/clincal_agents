# triage_ai_assistant/app/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Optional
from agents.triageagent import run_triage_workflow
from agents.nursebot import run_chat, handle_chat, NURSEBOT_SYSINT, WELCOME_MSG, llm_with_tools
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

app = FastAPI(title="AI Triage API")

class TriageRequest(BaseModel):
    note: str

class TriageResponse(BaseModel):
    esi: str
    diagnosis: str
    iterations: int

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]]

class ChatResponse(BaseModel):
    response: str
    finished: bool
    notes: Optional[List[str]] = None

@app.get("/")
def root():
    return {"message": "Triage API is running"}

@app.post("/triage", response_model=TriageResponse)
def triage_endpoint(data: TriageRequest):
    result = run_triage_workflow(data.note)
    return TriageResponse(**result)

# @app.post("/chat", response_model=ChatResponse)
# def chat_endpoint(data: ChatRequest):
#     # Initialize state if this is the first message
#     if not data.history:
#         return ChatResponse(
#             response=WELCOME_MSG,
#             finished=False,
#             notes=[]
#         )
    
#     # Convert history to the format expected by the LLM
#     messages = [SystemMessage(content=NURSEBOT_SYSINT[1])]
#     for msg in data.history:
#         if msg["role"] == "user":
#             messages.append(HumanMessage(content=msg["content"]))
#         elif msg["role"] == "assistant":
#             messages.append(AIMessage(content=msg["content"]))
    
#     # Get response from the LLM
#     response = llm_with_tools.invoke(messages)
    
#     # Extract notes if any
#     notes = []
#     if hasattr(response, "tool_calls") and response.tool_calls:
#         for call in response.tool_calls:
#             if call["name"] == "take_note" and "text" in call["args"]:
#                 notes.append(call["args"]["text"])
    
#     # Check if the chat should end
#     finished = any(word in data.message.lower() for word in ["thank you", "bye", "goodbye", "exit", "quit"])
    
#     return ChatResponse(
#         response=response.content,
#         finished=finished,
#         notes=notes
#     )

@app.post("/chat-to-triage", response_model=ChatResponse)
def chat_to_triage(data: ChatRequest):
    # Initialize state if this is the first message
    if not data.history:
        return ChatResponse(
            response=WELCOME_MSG,
            finished=False,
            notes=[]
        )
    
    # Convert history to the format expected by the LLM
    messages = [SystemMessage(content=NURSEBOT_SYSINT[1])]
    for msg in data.history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
    
    # Get response from the LLM
    response = llm_with_tools.invoke(messages)
    
    # Extract notes if any
    notes = []
    finished = False
    if hasattr(response, "tool_calls") and response.tool_calls:
        for call in response.tool_calls:
            if call["name"] == "take_note" and "text" in call["args"]:
                notes.append(call["args"]["text"])
                finished = True
    
    # If chat is finished, get triage assessment
    if finished:
        combined_note = "\n".join(notes)
        triage_result = run_triage_workflow(combined_note)
        return ChatResponse(
            response=f"Triage Assessment Complete!\nESI Level: {triage_result['esi']}\nDiagnosis: {triage_result['diagnosis']}",
            finished=True,
            notes=notes
        )
    
    return ChatResponse(
        response=response.content,
        finished=finished,
        notes=notes
    )
