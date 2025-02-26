from fastapi import APIRouter, HTTPException, status
from src.api.services.db_service import get_supabase_client
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/providers/by-user-id/{user_id}")
async def get_provider_by_user_id(user_id: str):
    """Get provider details by auth user ID."""
    try:
        supabase = get_supabase_client()
        
        # Query the providers table for this user_id
        response = supabase.table("providers") \
            .select("*") \
            .eq("user_id", user_id) \
            .single() \
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Provider not found"
            )
            
        return response.data
        
    except Exception as e:
        logger.error(f"Error fetching provider by user ID: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/providers")
async def list_providers():
    """List all providers."""
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("providers") \
            .select("*") \
            .execute()
            
        return response.data or []
        
    except Exception as e:
        logger.error(f"Error listing providers: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )