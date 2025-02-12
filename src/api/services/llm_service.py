from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain.chains import RetrievalQA
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

    def get_assessment_query(self, conversation_context: str, symptoms: str) -> str:
        """Generate assessment query template."""
        return f"""
        You are an experienced medical professional conducting an initial patient assessment. Based on the following conversation:

        {conversation_context}
        Latest message: {symptoms}

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

    def get_triage_query(self, conversation_context: str, symptoms: str) -> str:
        """Generate triage query template."""
        return f"""
        You are an experienced medical professional providing a triage assessment. Based on the following patient interaction:

        {conversation_context}
        Latest message: {symptoms}

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

    def process_query(self, query: str):
        """Process a query through the LLM chain."""
        return self.chain.invoke(query)