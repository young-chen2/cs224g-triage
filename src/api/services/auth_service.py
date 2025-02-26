from src.api.services.db_service import get_supabase_client
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

async def create_provider_account(email: str, password: str, role: str, name: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Create a new provider account with Supabase authentication.
    
    Args:
        email: Provider's email address
        password: Provider's password
        role: Provider role (physician, nurse, or pa)
        name: Provider's full name
        
    Returns:
        Tuple containing auth response and provider data
    """
    try:
        logger.info(f"Creating provider account for {email} with role {role}")
        supabase = get_supabase_client()
        
        # Create auth user
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if not auth_response.user:
            raise ValueError("Failed to create auth user")
            
        user_id = auth_response.user.id
        
        # Add provider details to the providers table
        provider_data = {
            "user_id": user_id,
            "name": name,
            "role": role,  # "physician", "nurse", or "pa"
            "created_at": "now()"
        }
        
        provider_response = supabase.table("providers").insert(provider_data).execute()
        
        if not provider_response.data:
            # If provider creation fails, try to clean up the auth user
            supabase.auth.admin.delete_user(user_id)
            raise ValueError("Failed to create provider record")
            
        logger.info(f"Successfully created provider account for {email}")
        return auth_response, provider_response.data[0]
        
    except Exception as e:
        logger.error(f"Error creating provider account: {str(e)}", exc_info=True)
        raise

async def provider_login(email: str, password: str) -> Dict[str, Any]:
    """
    Authenticate a provider using email and password.
    
    Args:
        email: Provider's email address
        password: Provider's password
        
    Returns:
        Authentication response data
    """
    try:
        logger.info(f"Attempting login for {email}")
        supabase = get_supabase_client()
        
        response = supabase.auth.sign_in_with_password({
            "email": email, 
            "password": password
        })
        
        if not response.user:
            raise ValueError("Invalid credentials")
            
        logger.info(f"Successful login for {email}")
        return {
            "user": response.user,
            "session": response.session,
            "access_token": response.session.access_token if response.session else None
        }
        
    except Exception as e:
        logger.error(f"Login error for {email}: {str(e)}", exc_info=True)
        raise

async def get_provider_by_user_id(user_id: str) -> Dict[str, Any]:
    """
    Get provider details from the providers table by user ID.
    
    Args:
        user_id: The auth user ID
        
    Returns:
        Provider details
    """
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("providers") \
            .select("*") \
            .eq("user_id", user_id) \
            .single() \
            .execute()
            
        if not response.data:
            raise ValueError(f"No provider found for user ID: {user_id}")
            
        return response.data
        
    except Exception as e:
        logger.error(f"Error fetching provider by user ID: {str(e)}", exc_info=True)
        raise

async def change_password(user_id: str, new_password: str) -> bool:
    """
    Change a user's password.
    
    Args:
        user_id: The auth user ID
        new_password: The new password
        
    Returns:
        True if successful, False otherwise
    """
    try:
        supabase = get_supabase_client()
        
        supabase.auth.admin.update_user_by_id(
            user_id,
            {"password": new_password}
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}", exc_info=True)
        return False