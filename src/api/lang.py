from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai import OpenAI
import json
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the absolute path to the project root directory
current_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the directory containing lang.py
root_dir = os.path.dirname(os.path.dirname(current_dir))  # Go up two levels to root

# Load environment variables with more verbose error handling
env_path = os.path.join(root_dir, '.env')
if not os.path.exists(env_path):
    raise FileNotFoundError(f"No .env file found at {env_path}")

load_dotenv(dotenv_path=env_path)
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("No OpenAI API key found in environment variables")

logger.info("Environment variables loaded successfully")

app = FastAPI()

# More permissive CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Your Next.js frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Explicitly allow OPTIONS
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,  # Cache preflight requests for 24 hours
)

def load_medical_data():
    triage_path = os.path.join(root_dir, 'DataTriage.json')
    guidelines_path = os.path.join(root_dir, 'Guidelines.json')
        
    with open(triage_path, 'r') as f:
        triage_data = json.load(f)
    
    with open(guidelines_path, 'r') as f:
        guidelines_data = json.load(f)
    
    # process data into text format for vectorization
    medical_texts = []
    
    # stringify triage data
    for category in triage_data:
        for case in triage_data[category]:
            text = f"Condition: {case['condition']}\n"
            text += f"Age Group: {case['age_group']}\n"
            text += f"Symptoms: {', '.join(case['symptoms'])}\n"
            text += f"ESI Level: {case['esi_level']}\n"
            medical_texts.append(text)
    
    # stringify guidelines data
    for category in guidelines_data:
        for case in guidelines_data[category]:
            text = f"Condition: {case['condition']}\n"
            text += f"Age Group: {case['age_group']}\n"
            text += f"ESI Level: {case['esi_level']}\n"
            text += f"Immediate Actions: {', '.join(case['guidelines']['immediate_actions'])}\n"
            text += f"Disposition Criteria: {', '.join(case['guidelines']['disposition_criteria'])}\n"
            medical_texts.append(text)
    
    return medical_texts

# Initialize LangChain components
embeddings = OpenAIEmbeddings(api_key=openai_api_key)

# Load or create FAISS index
index_path = os.path.join(root_dir, 'faiss_index')
if os.path.exists(index_path):
    logger.info("Loading existing FAISS index")
    vector_store = FAISS.load_local(index_path, embeddings)
else:
    logger.info("Creating new FAISS index")
    medical_texts = load_medical_data()
    vector_store = FAISS.from_texts(medical_texts, embeddings)
    # Save the index for future use
    vector_store.save_local(index_path)

# Modified chain to include source documents
chain = RetrievalQA.from_chain_type(
    llm=OpenAI(api_key=openai_api_key, temperature=0),
    chain_type="stuff",
    retriever=vector_store.as_retriever(),
    return_source_documents=True  # This will include the retrieved documents
)

class TriageRequest(BaseModel):
    symptoms: str
    conversation_history: list[dict]  # Add this field

class TriageResponse(BaseModel):
    symptoms_received: str
    raw_llm_response: str
    relevant_guidelines: list[str]
    is_gathering_info: bool  # Add this to indicate if more questions are needed

@app.post("/triage", response_model=TriageResponse)
async def triage_patient(request: TriageRequest):
    try:
        logger.info(f"Received triage request with symptoms: {request.symptoms}")
        
        # Format conversation history for context
        conversation_context = "\n".join([
            f"{'Assistant' if msg['role'] == 'assistant' else 'Patient'}: {msg['content']}"
            for msg in request.conversation_history[-5:]
        ])
        
        # Enhanced assessment query with medical professional tone and thorough information gathering
        assessment_query = f"""
        You are an experienced medical professional conducting an initial patient assessment. Based on the following conversation:

        {conversation_context}
        Latest message: {request.symptoms}

        Review the conversation and check if you have ALL of the following critical information:
        1. Patient's age
        2. Current symptoms and their duration
        3. Symptom severity
        4. Relevant medical history
        5. Current medications
        6. Allergies
        7. Recent injuries or medical procedures (if relevant)
        8. Any similar episodes in the past

        If ANY of this information is missing and relevant to the case, respond with:
        "NEED_INFO: [Ask a specific question in a professional, empathetic tone to gather the missing information]"

        Only respond with "READY_FOR_TRIAGE" if you have gathered all necessary information for a thorough assessment.

        Remember to:
        - Ask one clear question at a time
        - Maintain a professional and caring tone
        - Acknowledge the patient's concerns
        - Prioritize urgent symptoms in your questioning
        """
        
        assessment_response = chain.invoke(assessment_query)
        
        if "NEED_INFO:" in assessment_response['result']:
            return TriageResponse(
                symptoms_received=request.symptoms,
                raw_llm_response=assessment_response['result'].replace("NEED_INFO:", "").strip(),
                relevant_guidelines=[],
                is_gathering_info=True
            )
        
        # Enhanced triage query for comprehensive assessment
        triage_query = f"""
        You are an experienced medical professional providing a triage assessment. Based on the following patient interaction:

        {conversation_context}
        Latest message: {request.symptoms}

        Provide a structured triage assessment with the following format:

        1. Patient Profile:
           - Summarize key patient information (age, relevant history)
           - Primary symptoms and duration

        2. Assessment:
           - Most likely condition(s)
           - Severity assessment
           - ESI level (1-5) with brief justification

        3. Recommendations:
           - Immediate actions needed
           - Recommended care level (nurse, PA, doctor, or emergency room)
           - Timeframe for seeking care (immediate, within hours, within 24 hours, etc.)

        4. Additional Instructions:
           - Warning signs to watch for
           - Home care instructions (if applicable)
           - Follow-up recommendations

        Maintain a professional, clear, and empathetic tone. Prioritize patient safety and err on the side of caution when uncertain.
        """
        
        response = chain.invoke(triage_query)
        
        return TriageResponse(
            symptoms_received=request.symptoms,
            raw_llm_response=response['result'],
            relevant_guidelines=[doc.page_content for doc in response['source_documents']],
            is_gathering_info=False
        )
        
    except Exception as e:
        logger.error(f"Error processing triage request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request. Please try again."
        )

@app.get("/test")
async def test_triage():
    # sample test case for bacterial meningitis in children
    test_symptoms = "5-year-old child with high fever, severe headache, neck stiffness, and sensitivity to light"
    try:
        query = f"Given these symptoms: {test_symptoms}, what is the likely condition, ESI level, and recommended immediate actions?"
        response = chain.invoke(query)
        return {"test_symptoms": test_symptoms, "recommendation": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))