from fastapi import APIRouter, HTTPException
from src.api.models import TriageRequest, TriageResponse
from src.api.services.llm_service import LLMService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
llm_service = LLMService()

@router.post("/triage", response_model=TriageResponse)
async def triage_patient(request: TriageRequest):
    try:
        logger.info(f"Received triage request with symptoms: {request.symptoms}")
        
        # Format conversation history
        conversation_context = "\n".join([
            f"{'Assistant' if msg['role'] == 'assistant' else 'Patient'}: {msg['content']}"
            for msg in request.conversation_history[-5:]
        ])
        
        # Initial assessment
        assessment_query = llm_service.get_assessment_query(conversation_context, request.symptoms)
        assessment_response = llm_service.process_query(assessment_query)
        
        if "NEED_INFO:" in assessment_response['result']:
            return TriageResponse(
                symptoms_received=request.symptoms,
                raw_llm_response=assessment_response['result'].replace("NEED_INFO:", "").strip(),
                relevant_guidelines=[],
                is_gathering_info=True
            )
        
        # Full triage assessment
        triage_query = llm_service.get_triage_query(conversation_context, request.symptoms)
        response = llm_service.process_query(triage_query)
        
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