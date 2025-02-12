from pydantic import BaseModel

class TriageRequest(BaseModel):
    symptoms: str
    conversation_history: list[dict]

class TriageResponse(BaseModel):
    symptoms_received: str
    raw_llm_response: str
    relevant_guidelines: list[str]
    is_gathering_info: bool