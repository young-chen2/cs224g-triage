from src.api.services.db_service import get_supabase_client

async def create_provider_account(email: str, password: str, role: str, name: str):
    supabase = get_supabase_client()
    
    # Create auth user
    auth_response = supabase.auth.sign_up({
        "email": email,
        "password": password
    })
    
    user_id = auth_response.user.id
    
    # Add provider details to a providers table
    provider_data = {
        "user_id": user_id,
        "name": name,
        "role": role,  # "physician", "nurse", or "pa"
        "created_at": "now()"
    }
    
    provider_response = supabase.table("providers").insert(provider_data).execute()
    return auth_response, provider_response

async def provider_login(email: str, password: str):
    supabase = get_supabase_client()
    return supabase.auth.sign_in_with_password({"email": email, "password": password})