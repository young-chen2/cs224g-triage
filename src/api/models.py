from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import json
import uuid

class Message(BaseModel):
    role: str = Field(..., description="Role of the message sender (assistant or patient)")
    content: str = Field(..., description="Content of the message")

class TriageRequest(BaseModel):
    symptoms: str = Field(..., min_length=1, description="Patient's symptoms")
    conversation_history: List[Union[Message, Dict[str, str]]] = Field(default_factory=list)

class TriageResponse(BaseModel):
    """Response model for triage endpoint."""
    symptoms_received: str = Field(..., description="Symptoms that were processed")
    raw_llm_response: str = Field(..., description="Response from the LLM")
    relevant_guidelines: List[str] = Field(default_factory=list, description="Relevant medical guidelines used for triage")
    is_gathering_info: bool = Field(..., description="Whether the system is still gathering information or ready to make a triage decision")
    triage_level: Optional[str] = Field(None, description="Recommended triage level (physician, pa, nurse)")

class PatientInfo(BaseModel):
    """Model for patient information in API requests."""
    name: str = Field(..., description="Patient name")
    age: Optional[int] = Field(None, description="Patient age")
    gender: Optional[str] = Field(None, description="Patient gender")
    medical_history: Optional[str] = Field(None, description="Patient medical history")
    allergies: Optional[List[str]] = Field(default_factory=list, description="Patient allergies")
    medications: Optional[List[str]] = Field(default_factory=list, description="Current medications")
    
    class Config:
        extra = "allow"  # Allow additional fields

class PatientData(BaseModel):
    """Internal model for storing patient data in the database."""
    name: str
    dob: Optional[str] = None
    gender: Optional[str] = None
    contact_info: Optional[Dict[str, Any]] = None
    allergies: Optional[List[str]] = Field(default_factory=list, description="Patient allergies")
    medications: Optional[List[str]] = Field(default_factory=list, description="Current medications")
    
    class Config:
        extra = "allow"  # Allow additional fields

class ChatMessage(BaseModel):
    """Model for a chat message."""
    role: str = Field(..., description="Role of the message sender (user/assistant)")
    content: str = Field(..., description="Content of the message")
    
class TriageChatMessage(BaseModel):
    """Model for a chat message specifically in the triage system."""
    sender_type: str
    content: str

class TriageData(BaseModel):
    """Model for triage data storage in the database."""
    patient: PatientData
    triage_level: str
    summary: str
    chat_history: List[TriageChatMessage]

class TriageDataRequest(BaseModel):
    """Request model for completing a triage case."""
    patient_info: PatientInfo = Field(..., description="Patient information")
    symptoms: str = Field(..., description="Compiled symptoms from the conversation")
    chat_history: List[Dict[str, str]] = Field(..., description="Full chat history")
    triage_level: str = Field(..., description="Recommended triage level (physician, pa, nurse)")
    summary: Optional[str] = Field(None, description="Summary of the triage case")

class StatusUpdate(BaseModel):
    """Request model for updating case status."""
    status: str = Field(..., description="New status for the case (pending, in_progress, completed, cancelled)")

class ProviderCredentials(BaseModel):
    email: str
    password: str
    
class ProviderCreate(ProviderCredentials):
    name: str
    role: str

class ProviderInfo(BaseModel):
    """Model for provider information."""
    id: str = Field(..., description="Provider ID")
    name: str = Field(..., description="Provider name")
    role: str = Field(..., description="Provider role (physician, pa, nurse)")
    specialties: Optional[List[str]] = Field(default_factory=list, description="Provider specialties")

class CaseDetails(BaseModel):
    """Model for detailed case information."""
    id: str = Field(..., description="Case ID")
    patient_info: PatientInfo = Field(..., description="Patient information")
    triage_level: str = Field(..., description="Triage level")
    status: str = Field(..., description="Case status")
    creation_date: str = Field(..., description="Date and time the case was created")
    assigned_provider: Optional[ProviderInfo] = Field(None, description="Assigned provider")
    chat_history: List[Dict[str, str]] = Field(..., description="Chat history")
    summary: Optional[str] = Field(None, description="Case summary")

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