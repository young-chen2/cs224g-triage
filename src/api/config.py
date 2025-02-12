import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the absolute path to the project root directory
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))

# Load environment variables
env_path = os.path.join(root_dir, '.env')
if not os.path.exists(env_path):
    raise FileNotFoundError(f"No .env file found at {env_path}")

load_dotenv(dotenv_path=env_path)
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("No OpenAI API key found in environment variables")

# File paths
TRIAGE_PATH = os.path.join(root_dir, 'DataTriage.json')
GUIDELINES_PATH = os.path.join(root_dir, 'Guidelines.json')
FAISS_INDEX_PATH = os.path.join(root_dir, 'faiss_index')