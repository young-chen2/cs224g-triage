from fastapi import APIRouter, HTTPException, status, Depends
from src.api.models import *
from src.api.services.llm_service import BasicLLM, ConversationalLLM, TriageAgent
from src.prompts import get_assessment_query, get_assessment_query_v2, get_triage_query
import logging
from typing import List, Dict, Optional
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBasic()

# Use BasicLLM for initial assessment
llm_assessor = BasicLLM()
# Use ConversationalLLM with retrieval for final triage
llm_triager = ConversationalLLM()
res = llm_triager.process_query("I have weakness, confusion, cold and clammy skin, and a rapid heartbeat, and I am a 24-year-old female.")
logger.info(f'\nTEST RESULT:\n {res}')
# TriageAgent for database operations
triage_agent = TriageAgent()

# Simple authentication for demonstration purposes
def verify_credentials(credentials: Optional[HTTPBasicCredentials] = Depends(security)):
    # In a real app, you'd verify against the Supabase auth
    # This is a simple placeholder
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "password")
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

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
            for msg in request.conversation_history:
                # Convert to dict if it's a Message object
                if not isinstance(msg, dict):
                    if hasattr(msg, 'dict'):
                        msg = msg.dict()
                    elif hasattr(msg, 'model_dump'):
                        msg = msg.model_dump()
                
                # Validate dict structure
                if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                    conversation_messages.append({
                        'role': msg['role'],
                        'content': msg['content']
                    })
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
            # assessment_query = get_assessment_query(conversation_context, request.symptoms)
            assessment_query = get_assessment_query_v2(conversation_context, request.symptoms)
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
                
            # Check for READY_FOR_TRIAGE flag
            if "READY_FOR_TRIAGE" in assessment_result:
                logger.info("Assessment indicates ready for triage. Proceeding with final triage.")
            
            # Full triage assessment
            triage_query = get_triage_query(conversation_context, request.symptoms)
            triage_response = llm_triager.process_query(triage_query)
            
            if not isinstance(triage_response, dict):
                raise ValueError(f"Unexpected triage response type: {type(triage_response)}")
            
            # Extract triage level from response if available
            result_text = triage_response.get('result', '')
            triage_level = None
            
            logger.info(f'Here is the triange result: \n{result_text}')
            
            if "Recommended Care Level" in result_text:
                # Extract the triage level from the response
                triage_parts = result_text.split("Recommended Care Level")
                if len(triage_parts) > 1:
                    triage_level_line = triage_parts[1].strip().split("\n")[0]
                    if "physician" in triage_level_line.lower():
                        triage_level = "physician"
                    elif "pa" in triage_level_line.lower() or "physician assistant" in triage_level_line.lower():
                        triage_level = "pa"
                    elif "nurse" in triage_level_line.lower():
                        triage_level = "nurse"
            
            if not triage_level:
                # Default to physician for safety if we can't determine
                triage_level = "physician"
                
            # Clean the response for the user (remove the TRIAGE_LEVEL tag)
            clean_response = result_text
            clean_response = clean_response.replace("READY_FOR_TRIAGE", "").strip()
            
            # Ensure all fields are properly formatted
            response = TriageResponse(
                symptoms_received=request.symptoms,
                raw_llm_response=clean_response,
                relevant_guidelines=[
                    str(doc.page_content) if hasattr(doc, 'page_content') else str(doc)
                    for doc in triage_response.get('source_documents', [])
                ],
                is_gathering_info=False,
                triage_level=triage_level
            )
            
            return response
            
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
                    is_gathering_info=False,
                    triage_level="physician"
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

@router.post("/triage/complete")
async def complete_triage(triage_data: TriageDataRequest):
    """
    Save a completed triage case to the database.
    """
    try:
        logger.info(f"Processing complete triage with level: {triage_data.triage_level}")
        
        # Validate triage data
        if not triage_data.triage_level:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Triage level cannot be empty"
            )
            
        if not triage_data.symptoms:
            logger.warning("Symptoms field is empty in complete_triage request")
            
        # Process the triage through the TriageAgent
        result = await triage_agent.process_triage_result(
            patient_info=triage_data.patient_info,
            symptoms=triage_data.symptoms,
            chat_history=triage_data.chat_history,
            triage_level=triage_data.triage_level,
            summary=triage_data.summary
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('error', 'Failed to save triage case')
            )
            
        return {
            "message": "Triage case saved successfully",
            "case_id": result.get('case_id')
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing triage: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/providers/{provider_id}/cases", dependencies=[Depends(verify_credentials)])
async def get_provider_cases(provider_id: str, status: Optional[str] = None):
    """Get all triage cases for a specific provider."""
    try:
        cases = await triage_agent.get_provider_triage_cases(provider_id)
        
        # Filter by status if provided
        if status:
            cases = [case for case in cases if case.get('status') == status]
            
        return cases
    except Exception as e:
        logger.error(f"Error fetching provider cases: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/cases/{case_id}", dependencies=[Depends(verify_credentials)])
async def get_case_details(case_id: str):
    """Get full details of a specific triage case."""
    try:
        case_details = await triage_agent.get_case_details(case_id)
        
        if "error" in case_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=case_details["error"]
            )
            
        return case_details
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching case details: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.patch("/cases/{case_id}/status", dependencies=[Depends(verify_credentials)])
async def update_case_status(case_id: str, status_update: StatusUpdate):
    """Update the status of a triage case."""
    try:
        success = await triage_agent.update_case_status(case_id, status_update.status)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update case status"
            )
            
        return {"message": f"Case status updated to: {status_update.status}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating case status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )