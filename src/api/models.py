from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

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

class TriageDataRequest(BaseModel):
    patient_info: Dict[str, Any]
    symptoms: str
    triage_level: str
    chat_history: List[Dict[str, str]]
    summary: Optional[str] = None

# Status update
class StatusUpdate(BaseModel):
    status: str = Field(..., description="One of: pending, in_progress, completed")

# Dashboard data models
class TriageCase(BaseModel):
    id: str
    patient_id: str
    assigned_provider_id: Optional[str] = None
    status: str = "pending"
    triage_level: str
    summary: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
class MessageRecord(BaseModel):
    id: str
    triage_case_id: str
    sender_type: str
    message: str
    timestamp: datetime

