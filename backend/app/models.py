from pydantic import BaseModel
from typing import List, Dict, Optional

class MedicalTerm(BaseModel):
    term: str
    value: Optional[str] = None
    unit: Optional[str] = None
    explanation: str
    is_abnormal: bool = False
    status: Optional[str] = None 

class ReportAnalysis(BaseModel):
    extracted_text: str
    medical_terms: List[MedicalTerm]
    summary: str

class ChatRequest(BaseModel):
    question: str
    report_context: str
    chat_history: List[Dict[str, str]] = []

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    
class ValueCheckRequest(BaseModel):
    term: str
    value: float
    unit: str
    age: Optional[int] = None
    gender: Optional[str] = None
