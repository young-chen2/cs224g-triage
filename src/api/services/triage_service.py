from src.api.services.db_service import get_supabase_client
from typing import List, Dict, Any

async def create_triage_case(patient_data: Dict[str, Any], triage_level: str, summary: str, chat_history: List[Dict[str, Any]]):
    supabase = get_supabase_client()
    
    # 1. Create or get patient record
    patient_response = supabase.table("patients").upsert(patient_data).execute()
    patient_id = patient_response.data[0]["id"]
    
    # 2. Store the triage case
    case_data = {
        "patient_id": patient_id,
        "triage_level": triage_level,
        "summary": summary
    }
    
    case_response = supabase.table("triage_cases").insert(case_data).execute()
    case_id = case_response.data[0]["id"]
    
    # 3. Store the chat history
    for message in chat_history:
        message_data = {
            "triage_case_id": case_id,
            "sender_type": message["sender_type"],
            "message": message["content"]
        }
        supabase.table("chat_messages").insert(message_data).execute()
    
    # 4. Assign to appropriate provider based on triage level
    provider_response = supabase.table("providers") \
        .select("id") \
        .eq("role", triage_level) \
        .limit(1) \
        .execute()
    
    if provider_response.data:
        provider_id = provider_response.data[0]["id"]
        supabase.table("triage_cases") \
            .update({"assigned_provider_id": provider_id, "status": "pending"}) \
            .eq("id", case_id) \
            .execute()
    
    return {"case_id": case_id, "status": "triage_completed"}

async def get_provider_cases(provider_id: str, status: str = None):
    supabase = get_supabase_client()
    
    query = supabase.table("triage_cases") \
        .select("*, patients(name, dob, gender)") \
        .eq("assigned_provider_id", provider_id)
    
    if status:
        query = query.eq("status", status)
    
    response = query.execute()
    return response.data

async def get_case_messages(case_id: str):
    supabase = get_supabase_client()
    
    response = supabase.table("chat_messages") \
        .select("*") \
        .eq("triage_case_id", case_id) \
        .order("timestamp", desc=False) \
        .execute()
    
    return response.data