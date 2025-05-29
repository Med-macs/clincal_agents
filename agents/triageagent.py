# triage_ai_assistant/agents/triage_engine.py

from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
import re
# import os
# from dotenv import load_dotenv

# load_dotenv()

# Initialize Gemini model
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

# Enhanced prompt for the triage nurse
nurse_prompt = ChatPromptTemplate.from_template("""
You are an experienced ER triage nurse. Your task is to assess the Emergency Severity Index (ESI) for a new patient.

Patient Note: {note}
Doctor’s Previous Input (if any): {doctor_msg}

Step-by-step reasoning:
1. Summarize the key symptoms and risks.
2. Think aloud: Does this patient need immediate attention or tests?
3. Decide ESI level (1-5) with justification.
4. Reflect: Are you confident in this choice?

Your structured response:
Assessment:
ESI Level: X
Reasoning: ...
Confidence: High/Medium/Low
""")

# Enhanced prompt for the doctor
doctor_prompt = ChatPromptTemplate.from_template("""
You are an ER physician reviewing a triage assessment.

Patient Note: {note}
Nurse’s ESI Assessment:
{nurse_msg}

Step-by-step:
1. Restate main clinical concerns.
2. Do you agree with the ESI level? Why/why not?
3. If you disagree, suggest the correct ESI with reasoning.
4. Reflect on clarity and sufficiency of the nurse's reasoning.

Your structured response:
Assessment:
- Agreement: Yes/No
- Suggested ESI Level: X (if different)
- Reasoning: ...
- Comment: ...
""")

def extract_esi_from_response(response_text: str) -> dict:
    """Extract ESI level, reasoning, and confidence from structured LLM output"""
    esi_match = re.search(r'ESI\s*Level\s*[:\-]?\s*(\d)', response_text, re.IGNORECASE)
    reasoning_match = re.search(r'Reasoning\s*[:\-]?\s*(.*?)(?:Confidence|$)', response_text, re.IGNORECASE | re.DOTALL)
    confidence_match = re.search(r'Confidence\s*[:\-]?\s*(\w+)', response_text, re.IGNORECASE)

    return {
        "esi_level": int(esi_match.group(1)) if esi_match else None,
        "reasoning": reasoning_match.group(1).strip() if reasoning_match else "Unclear",
        "confidence": confidence_match.group(1) if confidence_match else "Unknown",
        "full_response": response_text
    }

def check_agreement(nurse_response: str, doctor_response: str) -> bool:
    """Check if doctor agrees with nurse's assessment"""
    if "agreement: yes" in doctor_response.lower():
        return True
    elif "agreement: no" in doctor_response.lower():
        return False

    nurse_esi = extract_esi_from_response(nurse_response).get("esi_level")
    doctor_esi = extract_esi_from_response(doctor_response).get("esi_level")
    return nurse_esi == doctor_esi if nurse_esi and doctor_esi else False

def nurse_step(state: Dict[str, Any]) -> Dict[str, Any]:
    inputs = {
        "note": state["note"],
        "doctor_msg": state.get("doctor_msg", "")
    }
    response = (nurse_prompt | llm).invoke(inputs)
    return {
        **state,
        "nurse_msg": response.content,
        "nurse_assessment": extract_esi_from_response(response.content)
    }

def doctor_step(state: Dict[str, Any]) -> Dict[str, Any]:
    inputs = {
        "note": state["note"],
        "nurse_msg": state["nurse_msg"]
    }
    response = (doctor_prompt | llm).invoke(inputs)
    agreement = check_agreement(state["nurse_msg"], response.content)

    return {
        **state,
        "doctor_msg": response.content,
        "doctor_assessment": extract_esi_from_response(response.content),
        "agreement": agreement,
        "iteration": state.get("iteration", 0) + 1
    }

def should_continue(state: Dict[str, Any]) -> str:
    """Decide whether to continue the loop or stop"""
    if state.get("iteration", 0) >= 2 or state.get("agreement", False):
        return END
    return "Nurse"

def get_final_esi(result: dict) -> dict:
    """Summarize final triage decision and reasoning"""
    nurse_esi = result.get("nurse_assessment", {}).get("esi_level")
    doctor_esi = result.get("doctor_assessment", {}).get("esi_level")
    agreement = result.get("agreement", False)

    if agreement and nurse_esi:
        final_esi = nurse_esi
        consensus = "Yes - Mutual Agreement"
    elif doctor_esi:
        final_esi = doctor_esi
        consensus = "No - Doctor Override"
    elif nurse_esi:
        final_esi = nurse_esi
        consensus = "No - Nurse Assessment Only"
    else:
        final_esi = "Unable to determine"
        consensus = "No consensus reached"

    esi_descriptions = {
        1: "Immediate - Life-threatening",
        2: "Emergent - High risk, don't delay",
        3: "Urgent - Stable but needs attention",
        4: "Less Urgent - Stable, minor issue",
        5: "Non-Urgent - Can wait"
    }

    return {
        "final_esi_level": final_esi,
        "esi_description": esi_descriptions.get(final_esi, "Assessment pending"),
        "consensus_reached": consensus,
        "nurse_reasoning": result.get("nurse_assessment", {}).get("reasoning", ""),
        "doctor_input": result.get("doctor_assessment", {}).get("reasoning", ""),
        "iterations_needed": result.get("iteration", 0)
    }

def generate_patient_friendly_summary(result: dict) -> str:
    """Convert clinical triage result to patient-friendly language"""
    level = result.get("final_esi_level", "unknown")
    desc = result.get("esi_description", "no information available")

    explanations = {
        1: "You need immediate medical attention. Our team is ready and will take care of you right away.",
        2: "You’re in a high-risk situation. You’ll be seen very soon to prevent any complications.",
        3: "You are stable but may need tests or procedures. Please stay comfortable while we prepare.",
        4: "You are not in immediate danger. You may need one or two simple tests.",
        5: "This is a minor issue. You can safely wait or consider seeing a general doctor later."
    }

    extra_note = "\nOur medical team will keep you informed and comfortable at every step."

    friendly_msg = f"""🩺 **Your Triage Result**

**Urgency Level:** {level}  
**What It Means:** {desc}  
{explanations.get(level, "We will assess you further shortly.")}

{extra_note}
"""
    return friendly_msg

# LangGraph workflow definition
workflow = StateGraph(state_schema=dict)
workflow.add_node("Nurse", nurse_step)
workflow.add_node("Doctor", doctor_step)
workflow.set_entry_point("Nurse")
workflow.add_edge("Nurse", "Doctor")
workflow.add_conditional_edges("Doctor", should_continue)

app = workflow.compile()

def run_triage_workflow(note: str) -> dict:
    """Run the entire triage conversation and return final result"""
    result = app.invoke({"note": note})
    return get_final_esi(result)

def display_esi_result(result: dict):
    """Console display for ESI outcome"""
    print("=" * 40)
    print("EMERGENCY SEVERITY INDEX (ESI) RESULT")
    print("=" * 40)
    print(f"ESI LEVEL: {result['final_esi_level']}")
    print(f"PRIORITY: {result['esi_description']}")
    print(f"CONSENSUS: {result['consensus_reached']}")
    print(f"ITERATIONS: {result['iterations_needed']}")
    print(f"\nNURSE REASONING:\n{result['nurse_reasoning'][:200]}...")
    print(f"\nDOCTOR INPUT:\n{result['doctor_input'][:200]}...")
    print("=" * 40)

if __name__ == "__main__":
    test_note = "45-year-old male presents with chest pain radiating to the left arm, shortness of breath, and sweating."
    print("Determining ESI level through nurse-doctor collaboration...\n")
    result = run_triage_workflow(test_note)
    display_esi_result(result)

    print("\n" + "-" * 40)
    print("PATIENT SUMMARY")
    print("-" * 40)
    print(generate_patient_friendly_summary(result))