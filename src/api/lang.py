from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.llms import OpenAI
import json
import os

# Get OpenAI API key from environment variable or hardcode it (not recommended for production)
openai_api_key = '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'
app = FastAPI()

# Allow CORS for your React frontend (replace 3000 with your frontend port)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# get the absolute path to the project root directory to local the .json files
current_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the directory containing lang.py
root_dir = os.path.dirname(os.path.dirname(current_dir))  # Go up two levels to root

def load_medical_data():
    triage_path = os.path.join(root_dir, 'DataTriage.json')
    guidelines_path = os.path.join(root_dir, 'Guidelines.json')
    
    # print(f"Looking for files in: {root_dir}")  
    # print(f"Triage path: {triage_path}")      
    # print(f"Guidelines path: {guidelines_path}") 
    
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
medical_texts = load_medical_data()
vector_store = FAISS.from_texts(medical_texts, embeddings)
chain = RetrievalQA.from_chain_type(
    llm=OpenAI(api_key=openai_api_key, temperature=0),
    chain_type="stuff",
    retriever=vector_store.as_retriever()
)
class TriageRequest(BaseModel):
    symptoms: str
class TriageResponse(BaseModel):
    recommendation: str

@app.post("/triage", response_model=TriageResponse)
async def triage_patient(request: TriageRequest):
    try:
        # Enhance the query to get more relevant results
        query = f"Given these symptoms: {request.symptoms}, what is the likely condition, ESI level, and recommended immediate actions?"
        response = chain.invoke(query)
        return {"recommendation": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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