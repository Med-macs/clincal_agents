from fastapi import APIRouter
from app.models import TriageRequest, TriageResponse, ChatRequest, ChatResponse
from app.engine import SessionDep
from agents.triageagent import run_triage_workflow
from agents.nursebot import NURSEBOT_SYSINT, WELCOME_MSG, llm_with_tools
from app.repository.AssessmentRepository import AssessmentRepository
import re
from app.logging import logger
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

TriageRouter = APIRouter(prefix="/triage")

# Prompt Injection Guard
def is_prompt_injection(input_text: str) -> bool:
    suspicious_phrases = [
        r"ignore\s+(all|previous|above)\s+instructions",
        r"disregard\s+(this|that|everything)",
        r"forget\s+.*\bprevious\b",
        r"act\s+as\s+.*",
        r"(system|you)\s+are\s+now",
        r"you\s+are\s+no\s+longer\s+an\s+AI"
    ]
    input_text_lower = input_text.lower()
    for pattern in suspicious_phrases:
        if re.search(pattern, input_text_lower):
            return True
    return False

def extract_esi_level(esi_str: str) -> int:
    try:
        match = re.search(r'ESI\s*(\d+)|Level\s*(\d+)', esi_str, re.IGNORECASE)
        if match:
            number = next(num for num in match.groups() if num is not None)
            return int(number)
        match = re.search(r'\d+', esi_str)
        if match:
            return int(match.group())
        logger.warning(f"Could not extract ESI level from '{esi_str}', using default value 3")
        return 3
    except Exception as e:
        logger.error(f"Error extracting ESI level from '{esi_str}': {e}")
        return 3


@TriageRouter.post("/", response_model=TriageResponse)
def triage_endpoint(data: TriageRequest, session: SessionDep):
    logger.info(f"Received triage request with note: {data.note}")
    if is_prompt_injection(data.note):
        logger.warning("Potential prompt injection detected in triage note")
        return TriageResponse(esi="N/A", diagnosis="Prompt injection detected", iterations=0)
    try:
        result = run_triage_workflow(data.note)
        logger.info(f"Triage workflow result: {result}")
        esi_level = extract_esi_level(result['esi'])
        assessment_repository = AssessmentRepository(session)
        assessment_id = assessment_repository.create(
            notes=data.note,
            esi_level=esi_level,
            diagnosis=result['diagnosis']
        )
        logger.info(f"Assessment stored successfully with ID: {assessment_id}")
    except Exception as e:
        logger.error(f"Error in triage endpoint: {e}")
        raise
    return TriageResponse(**result)

@TriageRouter.post("/chat", response_model=ChatResponse)
def chat_to_triage(data: ChatRequest, session: SessionDep):
    if not data.history:
        return ChatResponse(response=WELCOME_MSG, finished=False, notes=[])
    for msg in data.history:
        if is_prompt_injection(msg["content"]):
            logger.warning("Prompt injection detected in chat history")
            return ChatResponse(
                response="⚠️ Potential prompt injection detected. Conversation terminated for safety.",
                finished=True,
                notes=[]
            )
    messages = [SystemMessage(content=NURSEBOT_SYSINT[1])]
    for msg in data.history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
    response = llm_with_tools.invoke(messages)
    notes = []
    finished = False
    if hasattr(response, "tool_calls") and response.tool_calls:
        for call in response.tool_calls:
            if call["name"] == "take_note" and "text" in call["args"]:
                notes.append(call["args"]["text"])
                finished = True
    if finished:
        combined_note = "\n".join(notes)
        if is_prompt_injection(combined_note):
            logger.warning("Prompt injection detected in generated notes")
            return ChatResponse(
                response="⚠️ Unsafe content detected in final notes. Assessment aborted.",
                finished=True,
                notes=notes
            )
        triage_result = run_triage_workflow(combined_note)
        logger.info(f"Full triage result: {triage_result}")
        try:
            esi_level = extract_esi_level(triage_result['esi'])
            assessment_repository = AssessmentRepository(session)
            assessment_id = assessment_repository.create(
                notes=combined_note,
                esi_level=esi_level,
                diagnosis=triage_result['diagnosis']
            )
            logger.info(f"Chat assessment stored successfully with ID: {assessment_id}")
            return ChatResponse(
                response=f"Triage Assessment Complete!\nESI Level: {esi_level}\nDiagnosis: {triage_result['diagnosis']}\nAssessment ID: {assessment_id}",
                finished=True,
                notes=notes
            )
        except Exception as e:
            logger.error(f"Failed to store chat assessment: {e}")
            return ChatResponse(
                response=f"Triage Assessment Complete!\nESI Level: {triage_result['esi']}\nDiagnosis: {triage_result['diagnosis']}\nNote: Failed to store assessment",
                finished=True,
                notes=notes
            )
    return ChatResponse(response=response.content, finished=finished, notes=notes)