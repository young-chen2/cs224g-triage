from fastapi import APIRouter, HTTPException, status
from src.api.models import *
from src.api.services.llm_service import BasicLLM, ConversationalLLM
from src.api.services.prompts import get_assessment_query, get_triage_query
from src.api.services.triage_service import create_triage_case, get_provider_cases, get_case_messages
from src.api.services.auth_service import create_provider_account, provider_login
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)
router = APIRouter()

# Use BasicLLM for initial assessment
llm_assessor = BasicLLM()
# Use ConversationalLLM with retrieval for final triage
llm_triager = ConversationalLLM()

@router.post("/triage", response_model=TriageResponse)
async def triage_patient(request: TriageRequest) -> TriageResponse:
    """
    Process a triage request with proper validation and error handling.
    """
    try:
        logger.info(f"Received triage request with symptoms: {request.symptoms}")
        
        # Validate request
        if not request.symptoms.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Symptoms cannot be empty"
            )

        # Format conversation history with validation
        conversation_messages: List[Dict[str, str]] = []
        try:
            for msg in request.conversation_history[-10:]:  # Keep last 10 messages
                if not isinstance(msg, dict) and hasattr(msg, 'dict'):
                    msg = msg.dict()
                if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                    conversation_messages.append(msg)
        except Exception as e:
            logger.error(f"Error processing conversation history: {e}")
            conversation_messages = []  # Reset to empty if invalid

        conversation_context = "\n\n".join([
            f"{'###ASSISTANT###' if msg['role'] == 'assistant' else '###PATIENT###'}: {msg['content']}"
            for msg in conversation_messages
            if msg['content'].strip()  # Only include non-empty messages
        ])

        # Initial assessment with proper error handling
        try:
            assessment_query = get_assessment_query(conversation_context, request.symptoms)
            assessment_response = llm_assessor.process_query(assessment_query)
            
            if not isinstance(assessment_response, dict):
                raise ValueError(f"Unexpected assessment response type: {type(assessment_response)}")
                
            assessment_result = assessment_response.get('result')
            if not assessment_result:
                raise ValueError("Empty assessment result")
                
            if "NEED_INFO:" in assessment_result:
                return TriageResponse(
                    symptoms_received=request.symptoms,
                    raw_llm_response=assessment_result.replace("NEED_INFO:", "").strip(),
                    relevant_guidelines=[],
                    is_gathering_info=True
                )
            
            logger.info(f"Assessment complete. Proceeding with triage.")
            
            # Full triage assessment
            triage_query = get_triage_query(conversation_context, request.symptoms)
            triage_response = llm_triager.process_query(triage_query)
            
            if not isinstance(triage_response, dict):
                raise ValueError(f"Unexpected triage response type: {type(triage_response)}")
            
            # Ensure all fields are properly formatted
            return TriageResponse(
                symptoms_received=request.symptoms,
                raw_llm_response=str(triage_response.get('result', '')),
                relevant_guidelines=[
                    str(doc.page_content) if hasattr(doc, 'page_content') else str(doc)
                    for doc in triage_response.get('source_documents', [])
                ],
                is_gathering_info=False
            )
            
        except Exception as e:
            logger.error(f"Error in LLM processing: {str(e)}", exc_info=True)
            # Check for emergency symptoms even in case of error
            emergency_symptoms = [
                "stroke", "heart attack", "chest pain", "breathing",
                "unconscious", "severe bleeding", "head injury"
            ]
            if any(symptom in request.symptoms.lower() for symptom in emergency_symptoms):
                return TriageResponse(
                    symptoms_received=request.symptoms,
                    raw_llm_response="EMERGENCY: Please seek immediate medical attention or call emergency services (911).",
                    relevant_guidelines=[],
                    is_gathering_info=False
                )
            raise
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Triage request error: {str(e)}", exc_info=True)
        # Return a valid TriageResponse even in case of error
        return TriageResponse(
            symptoms_received=request.symptoms,
            raw_llm_response="I apologize, but I'm having trouble processing your request. If you're experiencing severe symptoms, please contact emergency services or your healthcare provider immediately.",
            relevant_guidelines=[],
            is_gathering_info=False
        )
        
@router.post("/auth/providers")
async def register_provider(provider_data: ProviderCreate):
    try:
        auth_response, provider_response = await create_provider_account(
            provider_data.email,
            provider_data.password,
            provider_data.role,
            provider_data.name
        )
        return {"message": "Provider created successfully", "provider_id": provider_response.data[0]["id"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/auth/login")
async def login(credentials: ProviderCredentials):
    try:
        response = await provider_login(credentials.email, credentials.password)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/triage/cases")
async def submit_triage(triage_data: TriageData):
    try:
        patient_dict = triage_data.patient.dict()
        chat_history = [message.dict() for message in triage_data.chat_history]
        
        result = await create_triage_case(
            patient_dict,
            triage_data.triage_level,
            triage_data.summary,
            chat_history
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/providers/{provider_id}/cases")
async def list_provider_cases(provider_id: str, status: str = None):
    try:
        cases = await get_provider_cases(provider_id, status)
        return cases
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/cases/{case_id}/messages")
async def list_case_messages(case_id: str):
    try:
        messages = await get_case_messages(case_id)
        return messages
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
