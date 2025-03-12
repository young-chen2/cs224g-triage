from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.api.services.db_service import get_supabase_client
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Verify the authentication token using Supabase authentication.
    
    Args:
        credentials: The HTTP Authorization credentials
        
    Returns:
        dict: User claims from the token
        
    Raises:
        HTTPException: If the token is invalid or expired
    """
    try:
        token = credentials.credentials
        supabase = get_supabase_client()
        
        # Verify the JWT token with Supabase
        user = supabase.auth.get_user(token)
        
        if not user or not user.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return user.user.model_dump()
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_provider(user_data: dict = Depends(verify_token)) -> dict:
    """
    Get the current provider based on the authenticated user.
    
    Args:
        user_data: The authenticated user data
        
    Returns:
        dict: Provider information
        
    Raises:
        HTTPException: If the provider is not found
    """
    try:
        user_id = user_data.get("id")
        if not user_id:
            raise ValueError("User ID not found in token")
            
        supabase = get_supabase_client()
        response = supabase.table("providers") \
            .select("*") \
            .eq("user_id", user_id) \
            .single() \
            .execute()
            
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Provider account not found"
            )
            
        return response.data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving provider: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve provider information"
        )