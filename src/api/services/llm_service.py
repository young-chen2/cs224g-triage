from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from src.api.config import openai_api_key, FAISS_INDEX_PATH
from src.api.services.medical_data import load_medical_data
import logging

logger = logging.getLogger(__name__)

class LLMService:
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
            llm=OpenAI(api_key=openai_api_key, temperature=0),
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(),
            return_source_documents=True
        )
        
        # return ConversationalRetrievalChain.from_llm(
        #     llm=OpenAI(api_key=openai_api_key, temperature=0),
        #     retriever=self.vector_store.as_retriever(),
        #     return_source_documents=True,
        #     memory=ConversationBufferMemory(
        #         memory_key="chat_history",
        #         return_messages=True
        #     ),
        #     chain_type="refine"  # or "map_reduce" for longer contexts
        # )

    def process_query(self, query: str):
        """Process a query through the LLM chain."""
        response =  self.chain.invoke(query)
        return response
    
        # Convert to the old format
        # return {
        #     'result': response['answer'],
        #     'source_documents': response['source_documents']
        # }
