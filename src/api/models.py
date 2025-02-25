from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

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
    
class PatientData(BaseModel):
    name: str
    dob: str = None
    gender: str = None
    contact_info: Dict[str, Any] = None

class ChatMessage(BaseModel):
    sender_type: str
    content: str

class TriageData(BaseModel):
    patient: PatientData
    triage_level: str
    summary: str
    chat_history: List[ChatMessage]

class ProviderCredentials(BaseModel):
    email: str
    password: str
    
class ProviderCreate(ProviderCredentials):
    name: str
    role: str
