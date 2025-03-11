from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from src.api.config import openai_api_key, FAISS_INDEX_PATH
from src.medical_data import load_medical_data
from src.api.models import PatientData, TriageData, TriageChatMessage
from src.api.services.db_service import get_supabase_client
from typing import Dict, Any, List, Tuple, Optional
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class BasicLLM:
   """Basic LLM for initial patient assessment without retrieval."""
   def __init__(self):
       self.llm = ChatOpenAI(
           api_key=openai_api_key,
           model="gpt-4o-mini",
           temperature=0,
           max_retries=3
       )
       self.chat_history: List[Tuple[str, str]] = []

   def process_query(self, query: str) -> Dict[str, Any]:
       """Process a query using the basic LLM."""
       try:
           # Construct messages array for chat completion
           messages = [
               SystemMessage(content="You are a medical triage assistant."),
               HumanMessage(content=query)
           ]
           
           # Add chat history if exists
           for past_query, past_response in self.chat_history:
               messages.extend([
                   HumanMessage(content=past_query),
                   AIMessage(content=past_response)
               ])
           
           # Get response from Chat API
           response = self.llm.invoke(messages)
           
           # Extract content from AIMessage
           response_text = response.content if hasattr(response, 'content') else str(response)
           
           # Update chat history
           self.chat_history.append((query, response_text))
           
           # Return in standardized format
           return {
               'result': response_text,
               'source_documents': []
           }
       except Exception as e:
           logger.error(f"Error in BasicLLM.process_query: {str(e)}", exc_info=True)
           # Specifically handle potential stroke symptoms
           if "slurred speech" in query.lower() and "face" in query.lower():
               emergency_response = ("EMERGENCY: These symptoms suggest a possible stroke. "
                                  "Please call emergency services (911) immediately. "
                                  "Do not wait for further assessment.")
               return {
                   'result': emergency_response,
                   'source_documents': []
               }
           raise

class LangChainBase:
   """Base class for retrieval-based LLM operations."""
   def __init__(self):
       self.embeddings = OpenAIEmbeddings(api_key=openai_api_key)
       self.vector_store = self._initialize_vector_store()
       self.chain = self._create_chain()

   def _initialize_vector_store(self):
       """Initialize or load FAISS vector store."""
       try:
           return FAISS.load_local(FAISS_INDEX_PATH, self.embeddings)
       except Exception as e:
           logger.info(f"Creating new FAISS index!!")
           medical_texts = load_medical_data()
           vector_store = FAISS.from_texts(medical_texts, self.embeddings)
           vector_store.save_local(FAISS_INDEX_PATH)
           return vector_store

   def _create_chain(self):
       """Create retrieval QA chain."""
       return RetrievalQA.from_chain_type(
           llm=ChatOpenAI(
               api_key=openai_api_key,
               model="gpt-4o-mini",
               temperature=0,
               max_retries=5,
               streaming=True
           ),
           chain_type="refine",
           retriever = self.vector_store.as_retriever(
                search_type="mmr",  # Maximal Marginal Relevance for diverse retrieval
                search_kwargs={"k": 10, "fetch_k": 50, "similarity_score_threshold": 0.75}
            ),
           return_source_documents=True
       )

   def process_query(self, query: str) -> Dict[str, Any]:
       """Process a query through the LLM chain."""
       response = self.chain.invoke(query)
       return {
           'result': response.get('answer', response.get('result', '')),
           'source_documents': response.get('source_documents', [])
       }

class ConversationalLLM(LangChainBase):
    """Conversational LLM with retrieval capabilities."""
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model="gpt-4o-mini",
            temperature=0,
            max_retries=3
        )
        self.chat_history: List[Tuple[str, str]] = []
        super().__init__()

    def _create_chain(self):
        """Override to create conversational retrieval chain."""
        return ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever = self.vector_store.as_retriever(
                search_type="mmr",  # Maximal Marginal Relevance for diverse retrieval
                search_kwargs={"k": 10, "fetch_k": 50, "similarity_score_threshold": 0.75}
            ),
            return_source_documents=True,
            verbose=True
        )

    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a query through the conversational LLM chain."""
        try:
            chain_input = {
                "question": query,
                "chat_history": self.chat_history
            }
            
            response = self.chain(chain_input)
            
            # Handle potential stroke symptoms immediately
            if ("slurred speech" in query.lower() and 
                "face" in query.lower() and 
                "weakness" in query.lower()):
                emergency_response = ("EMERGENCY: These symptoms suggest a possible stroke. "
                                   "Please call emergency services (911) immediately. "
                                   "Do not wait for further assessment.")
                return {
                    'result': emergency_response,
                    'source_documents': response.get('source_documents', [])
                }
            
            self.chat_history.append((query, response['answer']))
            
            return {
                'result': response['answer'],
                'source_documents': response.get('source_documents', [])
            }
            
        except Exception as e:
            logger.error(f"Error in ConversationalLLM.process_query: {str(e)}", exc_info=True)
            raise
        
class TriageAgent:
    """
    Agent that handles triage decision-making and database interactions.
    Handles post-triage actions like saving to database and routing to providers.
    """
    def __init__(self):
        self.llm = BasicLLM()  # For any additional reasoning
        self.supabase = get_supabase_client()

    async def process_triage_result(
        self, 
        patient_info: Dict[str, Any], 
        symptoms: str, 
        chat_history: List[Dict[str, str]], 
        triage_level: str, 
        summary: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a completed triage and store it in the database.
        
        Args:
            patient_info: Dictionary with patient information (name, dob, etc.)
            symptoms: The symptoms reported by the patient
            chat_history: List of messages exchanged during triage
            triage_level: Recommended provider type (physician, nurse, or pa)
            summary: Optional summary of the triage
            
        Returns:
            Dictionary with result of the operation
        """
        try:
            logger.info(f"Processing triage result for triage level: {triage_level}")
            
            # Convert PatientInfo to dict if it's a Pydantic model
            if hasattr(patient_info, 'dict'):
                patient_data_dict = patient_info.dict()
            elif hasattr(patient_info, 'model_dump'):  # For Pydantic v2
                patient_data_dict = patient_info.model_dump()
            else:
                # Assume it's already a dict
                patient_data_dict = patient_info
                
            # Extract allergies from patient info
            allergies = patient_data_dict.get('allergies', [])
            if isinstance(allergies, str):
                allergies = [allergies]
            
            # Prepare patient data
            patient_data = PatientData(
                name=patient_data_dict.get('name', 'Anonymous'),
                dob=patient_data_dict.get('dob', None),
                gender=patient_data_dict.get('gender', None),
                contact_info=patient_data_dict.get('contact_info', {}),
                allergies=allergies,
                medications=patient_data_dict.get('medications', [])
            )
            
            # Format for database
            formatted_patient = {
                "name": patient_data.name,
                "dob": patient_data.dob,
                "gender": patient_data.gender,
                "contact_info": json.dumps(patient_data.contact_info) if patient_data.contact_info else None,
                "allergies": json.dumps(patient_data.allergies) if patient_data.allergies else None,
                "medications": json.dumps(patient_data.medications) if patient_data.medications else None
            }
            
            # 1. Create patient record
            patient_response =  self.supabase.table("patients").upsert(formatted_patient).execute()
            if not patient_response.data:
                raise Exception("Failed to create patient record")
                
            patient_id = patient_response.data[0]["id"]
            
            # Generate summary if not provided
            if not summary:
                summary_query = f"""
                Based on the patient's symptoms: {symptoms}
                And their triage level: {triage_level}
                Provide a brief (1-2 sentence) summary of this triage case.
                """
                summary_response = self.llm.process_query(summary_query)
                summary = summary_response.get('result', 'Triage completed via AI assistant')
            
            # 2. Format chat history
            formatted_chat_history = []
            for msg in chat_history:
                if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                    formatted_chat_history.append(
                        TriageChatMessage(
                            sender_type="patient" if msg['role'] == "user" else "system",
                            content=msg['content']
                        )
                    )
            
            # 3. Create triage data
            triage_data = TriageData(
                patient=patient_data,
                triage_level=triage_level,
                summary=summary,
                chat_history=formatted_chat_history
            )
            
            # 4. Format for database
            case_data = {
                "patient_id": patient_id,
                "triage_level": triage_level.lower(),
                "summary": triage_data.summary,
                "status": "pending"
            }
            
            # 5. Create triage case
            case_response =  self.supabase.table("triage_cases").insert(case_data).execute()
            if not case_response.data:
                raise Exception("Failed to create triage case")
                
            case_id = case_response.data[0]["id"]
            
            # 6. Store chat messages
            for message in chat_history:
                msg_data = {
                    "triage_case_id": case_id,
                    "sender_type": "patient" if message["role"] == "user" else "system",
                    "message": message["content"],
                    "timestamp": datetime.utcnow().isoformat()
                }
                self.supabase.table("chat_messages").insert(msg_data).execute()
            
            # 7. Assign to provider based on triage level
            provider_response =  self.supabase.table("providers") \
                .select("id") \
                .eq("role", triage_level.lower()) \
                .limit(1) \
                .execute()
                
            if provider_response.data:
                provider_id = provider_response.data[0]["id"]
                self.supabase.table("triage_cases") \
                    .update({"assigned_provider_id": provider_id}) \
                    .eq("id", case_id) \
                    .execute()
            
            logger.info(f"Triage case {case_id} created and assigned successfully")
            
            return {
                "success": True,
                "case_id": case_id,
                "patient_id": patient_id,
                "provider_id": provider_response.data[0]["id"] if provider_response.data else None
            }
            
        except Exception as e:
            logger.error(f"Error in TriageAgent.process_triage_result: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_provider_triage_cases(self, provider_id: str) -> List[Dict[str, Any]]:
        """Get all triage cases assigned to a provider."""
        try:
            response =  self.supabase.table("triage_cases") \
                .select("*, patients(name, dob, gender)") \
                .eq("assigned_provider_id", provider_id) \
                .execute()
                
            return response.data or []
        except Exception as e:
            logger.error(f"Error getting provider cases: {str(e)}", exc_info=True)
            return []
    
    async def get_case_details(self, case_id: str) -> Dict[str, Any]:
        """Get full details of a specific triage case."""
        try:
            # Get case details
            case_response =  self.supabase.table("triage_cases") \
                .select("*, patients(*)") \
                .eq("id", case_id) \
                .single() \
                .execute()
                
            if not case_response.data:
                return {"error": "Case not found"}
                
            # Get chat messages
            messages_response =  self.supabase.table("chat_messages") \
                .select("*") \
                .eq("triage_case_id", case_id) \
                .order("timestamp", {"ascending": True}) \
                .execute()
                
            # Combine data
            return {
                "case": case_response.data,
                "messages": messages_response.data or []
            }
        except Exception as e:
            logger.error(f"Error getting case details: {str(e)}", exc_info=True)
            return {"error": str(e)}
    
    async def update_case_status(self, case_id: str, status: str) -> bool:
        """Update the status of a triage case."""
        try:
            self.supabase.table("triage_cases") \
                .update({"status": status}) \
                .eq("id", case_id) \
                .execute()
                
            return True
        except Exception as e:
            logger.error(f"Error updating case status: {str(e)}", exc_info=True)
            return False