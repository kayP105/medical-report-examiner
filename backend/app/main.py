from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import logging

from app.config import get_settings
from app.models import ReportAnalysis, ChatRequest, ChatResponse, ValueCheckRequest, MedicalTerm
from app.pdf_processor import PDFProcessor
from app.value_analyzer import ValueAnalyzer
from app.rag_pipeline import MedicalRAGPipeline


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(title="Medical Report Explainer API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


settings = get_settings()
pdf_processor = PDFProcessor()
value_analyzer = ValueAnalyzer()
rag_pipeline = None


@app.on_event("startup")
async def startup_event():
    """Initialize RAG pipeline on startup"""
    global rag_pipeline
    
    try:
        if not settings.OPENAI_API_KEY:
            logger.warning("⚠️ OpenAI API key not set!")
            return
        
        knowledge_path = "data/medical_knowledge.txt"
        if not os.path.exists(knowledge_path):
            logger.error(f"❌ File not found: {knowledge_path}")
            return
            
        with open(knowledge_path, 'r', encoding='utf-8') as f:
            medical_docs = [f.read()]
        
        logger.info("🚀 Initializing RAG pipeline...")
        rag_pipeline = MedicalRAGPipeline(settings)
        
        if os.path.exists("vector_db/medical_knowledge"):
            logger.info("📂 Loading knowledge base...")
            rag_pipeline.load_knowledge_base()
        else:
            logger.info("🔨 Building knowledge base...")
            rag_pipeline.build_knowledge_base(medical_docs)
        
        rag_pipeline.setup_qa_chain()
        logger.info("✅ RAG pipeline ready!")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


@app.get("/")
async def root():
    return {
        "message": "Medical Report Explainer API",
        "status": "running",
        "rag_initialized": rag_pipeline is not None
    }


@app.post("/upload-report", response_model=ReportAnalysis)
async def upload_report(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    temp_path = f"temp_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Processing: {file.filename}")
        extracted_text = pdf_processor.extract_text_from_pdf(temp_path)
        cleaned_text = pdf_processor.clean_text(extracted_text)
        gender = None
        if any(x in cleaned_text.lower() for x in [' female', '/f', 'f/', ' f ']):
            gender = 'female'
        elif any(x in cleaned_text.lower() for x in [' male', '/m', 'm/', ' m ']):
            gender = 'male'
        logger.info(f"Detected gender: {gender}")
        terms_data = pdf_processor.extract_medical_terms(cleaned_text)
        logger.info(f"Found {len(terms_data)} medical terms")

        medical_terms = []
        for term_data in terms_data:
            try:
                explanation = rag_pipeline.explain_term(
                    term_data['term'],
                    term_data['context']
                )
                
                status_info = {"is_abnormal": False}
                if term_data['value']:
                    try:
                        value_float = float(term_data['value'])
                        status_info = value_analyzer.analyze_value(
                            term_data['term'],
                            value_float,
                            term_data['unit'],
                            gender=gender
                        )
                    except ValueError:
                        logger.warning(f"Could not parse value: {term_data['value']}")
                
                medical_terms.append(MedicalTerm(
                    term=term_data['term'],
                    value=term_data['value'],
                    unit=term_data['unit'],
                    explanation=explanation,
                    is_abnormal=status_info.get('is_abnormal', False),
                    status=status_info.get('status')
                ))
                
            except Exception as e:
                logger.error(f"Error processing {term_data['term']}: {e}")
                continue
        

        logger.info("Generating key findings summary...")
        
        abnormal_findings = [
            f"{term.term} is {term.status.upper()} at {term.value} {term.unit}"
            for term in medical_terms
            if term.is_abnormal and term.value
        ]
        
        normal_findings = [
            f"{term.term}: {term.value} {term.unit}"
            for term in medical_terms
            if not term.is_abnormal and term.value
        ]
        
        findings_summary = f"""Test Results Summary:
- Total tests: {len(medical_terms)}
- Abnormal values: {len(abnormal_findings)}
- Normal values: {len(normal_findings)}

Key Abnormal Results:
{chr(10).join(['• ' + f for f in abnormal_findings[:5]]) if abnormal_findings else '• All values within normal range'}

Sample Normal Results:
{chr(10).join(['• ' + f for f in normal_findings[:3]]) if normal_findings else ''}
"""
        
        summary_prompt = f"""You are a medical assistant. Based on this blood test report, write a clear summary in 4-5 bullet points for the patient.

{findings_summary}

Report Context:
{cleaned_text[:500]}

Write 4-5 bullet points that:
• State what type of tests were performed
• Highlight any abnormal values and briefly explain what they might indicate
• Mention important normal values
• Suggest next steps or what to discuss with doctor

Use simple, empathetic English. Format as bullet points starting with •."""
        
        try:
            summary_result = rag_pipeline.answer_question(summary_prompt, cleaned_text[:400])
            summary_text = summary_result['answer']
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            summary_text = f"""• Complete Blood Count (CBC) and related tests were performed to assess your overall health.
• {len(abnormal_findings)} value(s) are outside normal range: {', '.join([f.split(' is ')[0] for f in abnormal_findings[:3]])}
• {len(normal_findings)} value(s) are within normal limits, which is positive.
• Please consult your doctor to discuss these results and determine next steps."""
        
        return ReportAnalysis(
            extracted_text=cleaned_text[:1000],
            medical_terms=medical_terms,
            summary=summary_text
        )
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="RAG not initialized")
    
    try:
        result = rag_pipeline.answer_question(
            request.question,
            request.report_context
        )
        
        return ChatResponse(
            answer=result['answer'],
            sources=result['sources'][:3]
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/check-value")
async def check_value(request: ValueCheckRequest):
    try:
        result = value_analyzer.analyze_value(
            request.term,
            request.value,
            request.unit,
            request.age,
            request.gender
        )
        return result
    except Exception as e:
        logger.error(f"Value check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
