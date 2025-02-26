from fastapi import APIRouter, HTTPException, status
from src.api.models import ProviderCredentials, ProviderCreate
from src.api.services.auth_service import create_provider_account, provider_login
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/auth/providers")
async def register_provider(provider_data: ProviderCreate):
    """
    Register a new provider account.
    """
    try:
        # Validate role
        valid_roles = ["physician", "nurse", "pa"]
        if provider_data.role.lower() not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role must be one of: {', '.join(valid_roles)}"
            )
        
        auth_response, provider_response = await create_provider_account(
            provider_data.email,
            provider_data.password,
            provider_data.role.lower(),
            provider_data.name
        )
        
        return {
            "message": "Provider created successfully", 
            "provider_id": provider_response["id"]
        }
        
    except ValueError as e:
        logger.error(f"Validation error in provider registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in provider registration: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create provider account"
        )

@router.post("/auth/login")
async def login(credentials: ProviderCredentials):
    """
    Authenticate a provider and return session data.
    """
    try:
        response = await provider_login(credentials.email, credentials.password)
        return response
        
    except ValueError as e:
        logger.error(f"Login validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )