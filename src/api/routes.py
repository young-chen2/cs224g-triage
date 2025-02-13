from fastapi import APIRouter, HTTPException
from src.api.models import TriageRequest, TriageResponse
from src.api.services.llm_service import LLMService
from src.api.services.prompts import get_assessment_query, get_triage_query
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
llm_assessor= LLMService()
llm_triager = LLMService()

@router.post("/triage", response_model=TriageResponse)
async def triage_patient(request: TriageRequest):
    try:
        logger.info(f"Received the following message from patient: {request.symptoms}")
        
        # Format conversation history
        conversation_context = "\n\n".join([
            f"{'###ASSISTANT###' if msg['role'] == 'assistant' else '###PATIENT###'}: {msg['content']}"
            for msg in request.conversation_history[-10:]
        ])
        
        print(conversation_context)
        
        # Initial assessment
        assessment_query = get_assessment_query(conversation_context, request.symptoms)
        assessment_response = llm_assessor.process_query(assessment_query)
        
        if "NEED_INFO:" in assessment_response['result']:
            return TriageResponse(
                symptoms_received=request.symptoms,
                raw_llm_response=assessment_response['result'].replace("NEED_INFO:", "").strip(),
                relevant_guidelines=[],
                is_gathering_info=True
            )
        
        logger.info(f"Received response from assessment agent: {assessment_response['result']}")
        
        # Full triage assessment
        triage_query = get_triage_query(conversation_context, request.symptoms)
        response = llm_triager.process_query(triage_query)
        
        return TriageResponse(
            symptoms_received=request.symptoms,
            raw_llm_response=response['result'],
            relevant_guidelines=[doc.page_content for doc in response['source_documents']],
            is_gathering_info=False
        )
        
    except Exception as e:
        logger.error(f"Error processing triage request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request. Please try again."
        )