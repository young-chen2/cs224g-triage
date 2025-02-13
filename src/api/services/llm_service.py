from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from src.api.config import openai_api_key, FAISS_INDEX_PATH
from src.api.services.medical_data import load_medical_data
from typing import Dict, Any, List, Tuple
import logging

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
           logger.info(f"Creating new FAISS index: {str(e)}")
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
               max_retries=3
           ),
           chain_type="stuff",
           retriever=self.vector_store.as_retriever(),
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
        )
        self.chat_history: List[Tuple[str, str]] = []
        super().__init__()

    def _create_chain(self):
        """Override to create conversational retrieval chain."""
        return ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vector_store.as_retriever(
                search_kwargs={"k": 3}  # Limit to top 3 most relevant documents
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