from supabase import create_client, Client
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get Supabase credentials
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# Check if credentials are available
if not supabase_url or not supabase_key:
    logger.warning("Supabase credentials not found in environment variables. Using default values.")
    # Fallback to default values (replace these with your actual values)
    supabase_url = "YOUR_SUPABASE_URL"
    supabase_key = "YOUR_SUPABASE_KEY"

# Initialize the Supabase client
supabase: Client = None

def get_supabase_client() -> Client:
    """
    Get or initialize the Supabase client.
    Returns a singleton instance of the Supabase client.
    """
    global supabase
    if supabase is None:
        try:
            supabase = create_client(supabase_url, supabase_key)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            raise
    
    return supabase

# Initialize tables if they don't exist (only needed for development)
async def initialize_tables():
    """
    Initialize database tables if they don't exist.
    This is mainly for development purposes.
    """
    try:
        client = get_supabase_client()
        
        # Create providers table
        await client.table("providers").create({
            "id": "uuid primary key default uuid_generate_v4()",
            "user_id": "uuid references auth.users not null",
            "name": "text not null",
            "role": "text not null check (role in ('physician', 'nurse', 'pa'))",
            "created_at": "timestamp with time zone default now()"
        }).execute()
        
        # Create patients table
        await client.table("patients").create({
            "id": "uuid primary key default uuid_generate_v4()",
            "name": "text not null",
            "dob": "date",
            "gender": "text",
            "contact_info": "jsonb",
            "created_at": "timestamp with time zone default now()"
        }).execute()
        
        # Create triage_cases table
        await client.table("triage_cases").create({
            "id": "uuid primary key default uuid_generate_v4()",
            "patient_id": "uuid references patients not null",
            "assigned_provider_id": "uuid references providers",
            "status": "text default 'pending' check (status in ('pending', 'in_progress', 'completed'))",
            "triage_level": "text not null check (triage_level in ('physician', 'nurse', 'pa'))",
            "summary": "text",
            "created_at": "timestamp with time zone default now()",
            "updated_at": "timestamp with time zone default now()"
        }).execute()
        
        # Create chat_messages table
        await client.table("chat_messages").create({
            "id": "uuid primary key default uuid_generate_v4()",
            "triage_case_id": "uuid references triage_cases not null",
            "sender_type": "text not null check (sender_type in ('patient', 'system'))",
            "message": "text not null",
            "timestamp": "timestamp with time zone default now()"
        }).execute()
        
        logger.info("Tables initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing tables: {str(e)}")