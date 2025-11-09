import os
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from typing import List, Dict
import logging


logger = logging.getLogger(__name__)


class MedicalRAGPipeline:
    """RAG pipeline for medical knowledge retrieval and question answering"""
    
    def __init__(self, config):
        self.config = config
        
        os.environ["GOOGLE_API_KEY"] = config.OPENAI_API_KEY
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name=config.EMBEDDING_MODEL
        )
        self.vector_store = None
        self.qa_chain = None
        
     
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            temperature=config.TEMPERATURE,
            convert_system_message_to_human=True
        )
        
    def build_knowledge_base(self, documents: List[str]):
        """Build FAISS vector store from medical documents"""
        logger.info("Building knowledge base...")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP,
            length_function=len,
        )
        
        texts = []
        for doc in documents:
            chunks = text_splitter.split_text(doc)
            texts.extend(chunks)
        
        logger.info(f"Created {len(texts)} text chunks")
        
        self.vector_store = FAISS.from_texts(
            texts=texts,
            embedding=self.embeddings
        )
        
        os.makedirs("vector_db", exist_ok=True)
        self.vector_store.save_local("vector_db/medical_knowledge")
        logger.info("Vector store saved successfully")
        
    def load_knowledge_base(self):
        """Load existing vector store"""
        try:
            self.vector_store = FAISS.load_local(
                "vector_db/medical_knowledge",
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            logger.info("Vector store loaded successfully")
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            raise
    
    def setup_qa_chain(self):
        """Setup conversational QA chain"""
        
        prompt_template = """You are a helpful medical assistant that explains medical terms and reports in simple English.
        Use the following context from medical knowledge base and the patient's report to answer the question.
        
        Context from knowledge base:
        {context}
        
        Chat History:
        {chat_history}
        
        Question: {question}
        
        Instructions:
        - CRITICAL: Respond ONLY in English, never in French or other languages
        - Explain medical terms in simple, easy-to-understand language
        - If discussing lab values, mention whether they're normal, high, or low
        - Be empathetic and clear
        - If you don't have enough information, say "I don't have enough information about [topic] in the provided context"
        - Keep explanations concise (2-3 sentences)
        
        Answer in English:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "chat_history", "question"]
        )
        
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vector_store.as_retriever(
                search_kwargs={"k": self.config.TOP_K_RESULTS}
            ),
            memory=memory,
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": PROMPT}
        )
        
        logger.info("QA chain setup complete")
    
    def explain_term(self, term: str, context: str = "") -> str:
        """Explain a medical term in simple language"""
        try:
            query = f"Explain what {term} means in simple English. Be specific and concise (2-3 sentences)."
            if context:
                query += f" Context from patient report: {context[:200]}"
            
            result = self.qa_chain({"question": query})
            answer = result["answer"]
            
           
            french_indicators = ['est', 'sont', 'votre', 'vous', 'pour', 'dans']
            if any(word in answer.lower().split() for word in french_indicators):
                logger.warning(f"French response detected for {term}, retrying...")
               
                query = f"IN ENGLISH ONLY: What is {term}? Explain briefly."
                result = self.qa_chain({"question": query})
                answer = result["answer"]
            
            return answer
            
        except Exception as e:
            logger.error(f"Error explaining {term}: {e}")
         
            return f"A {term} is a medical test that measures specific values in your blood to assess your health."
    
    def answer_question(self, question: str, report_context: str = "") -> Dict:
        """Answer a question about the medical report"""
        try:
            full_question = f"Answer in English: {question}"
            if report_context:
                full_question = f"Based on this medical report excerpt: {report_context[:400]}...\n\nQuestion (answer in English): {question}"
            
            result = self.qa_chain({"question": full_question})
            
            return {
                "answer": result["answer"],
                "sources": [doc.page_content for doc in result.get("source_documents", [])]
            }
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                "answer": "I'm having trouble answering this question. Please try rephrasing it.",
                "sources": []
            }
