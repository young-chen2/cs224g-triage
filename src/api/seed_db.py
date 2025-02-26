import logging
import time
from src.api.services.db_service import get_supabase_client
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if dev mode is enabled
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

def seed_database():
    """
    Seed the database with test provider accounts.
    
    This script creates test accounts for physician, nurse, and PA roles.
    """
    logger.info("Starting database seeding...")
    
    # First, check if we can connect to Supabase
    try:
        supabase = get_supabase_client()
        # Test connection with a simple query
        test_query = supabase.table("providers").select("count", count="exact").execute()
        provider_count = test_query.count if hasattr(test_query, 'count') else 0
        logger.info(f"Connected to Supabase. Current provider count: {provider_count}")
    except Exception as e:
        logger.error(f"Failed to connect to Supabase: {str(e)}")
        logger.error("Please check your Supabase credentials and connectivity")
        return
    
    # Define test accounts to create
    test_providers = [
        {
            "email": "doctor@example.com",
            "password": "password123",
            "name": "Dr. Jane Smith",
            "role": "physician"
        },
        {
            "email": "nurse@example.com",
            "password": "password123",
            "name": "Nurse Robert Johnson",
            "role": "nurse"
        },
        {
            "email": "pa@example.com",
            "password": "password123",
            "name": "PA Maria Garcia",
            "role": "pa"
        }
    ]
    
    created_count = 0
    
    for provider in test_providers:
        try:
            logger.info(f"Creating test provider: {provider['email']}")
            
            # For dev mode, just log that we're simulating
            if DEV_MODE:
                logger.info(f"DEV MODE: Simulating creation of {provider['email']}")
                created_count += 1
                continue
                
            # Check if email already exists to avoid duplicates
            try:
                admin_client = supabase.auth.admin
                existing_users = admin_client.list_users()
                email_exists = any(user.email == provider["email"] for user in existing_users)
                
                if email_exists:
                    logger.info(f"User with email {provider['email']} already exists, skipping...")
                    continue
            except Exception as e:
                logger.warning(f"Couldn't check for existing user: {e}")
                # Continue anyway
            
            # Create auth user
            auth_response = supabase.auth.sign_up({
                "email": provider["email"],
                "password": provider["password"],
                "options": {
                    "data": {
                        "name": provider["name"],
                        "role": provider["role"]
                    }
                }
            })
            
            if not auth_response.user:
                logger.error(f"Failed to create auth user for {provider['email']}")
                continue
                
            user_id = auth_response.user.id
            
            # Add provider details to providers table
            provider_data = {
                "user_id": user_id,
                "name": provider["name"],
                "role": provider["role"],
                "created_at": "now()"
            }
            
            provider_response = supabase.table("providers").insert(provider_data).execute()
            
            if not provider_response.data:
                logger.error(f"Failed to create provider record for {provider['email']}")
                # Try to clean up auth user
                try:
                    supabase.auth.admin.delete_user(user_id)
                except:
                    pass
                continue
                
            logger.info(f"Successfully created provider: {provider['email']} with ID: {provider_response.data[0]['id']}")
            created_count += 1
            
            # Sleep to avoid rate limits
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Error creating provider {provider['email']}: {str(e)}")
    
    logger.info(f"Database seeding complete. Created {created_count} provider accounts.")

if __name__ == "__main__":
    seed_database()