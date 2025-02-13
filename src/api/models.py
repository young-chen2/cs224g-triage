from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class Message(BaseModel):
    role: str = Field(..., description="Role of the message sender (assistant or patient)")
    content: str = Field(..., description="Content of the message")

class TriageRequest(BaseModel):
    symptoms: str = Field(..., min_length=1, description="Patient's symptoms")
    conversation_history: List[Message] = Field(default_factory=list, description="Conversation history")

class TriageResponse(BaseModel):
    symptoms_received: str
    raw_llm_response: str
    relevant_guidelines: List[str]
    is_gathering_info: bool