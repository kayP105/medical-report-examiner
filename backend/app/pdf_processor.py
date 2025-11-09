import pdfplumber
import re
from typing import List, Dict, Tuple
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFProcessor:
    """Extract text and medical terms from PDF reports"""

    MEDICAL_PATTERNS = {

        'CBC': r'\b(CBC|Complete Blood Count)\b',
        'Hemoglobin': r'\b(Haemoglobin|Hemoglobin|HGB|Hgb)\b',
        'WBC': r'\b(WBC Count|WBC|White Blood Cell)\b',
        'RBC': r'\b(RBC Count|RBC|Red Blood Cell)\b',
        'Platelets': r'\b(Platelet Count|Platelet)\b',
        'Hematocrit': r'\b(Hematocrit|HCT|PCV|Packed Cell Volume)\b',
        'MCV': r'\b(MCV|Mean Corpuscular Volume)\b',
        'MCH': r'\b(MCH|Mean Corpuscular Hemoglobin)\b',
        'MCHC': r'\b(MCHC|Mean Corpuscular Hemoglobin Concentration)\b',
        'RDW': r'\b(RDW|Red Cell Distribution Width|Red Distribution Width)\b',
        'MPV': r'\b(MPV|Mean Platelet Volume)\b',
        
       
        'Differential Count': r'\b(Differential Count)\b',
        'Neutrophils': r'\b(Neutrophil)\b',
        'Lymphocytes': r'\b(Lymphocyte)\b',
        'Eosinophils': r'\b(Eosinophil)\b',
        'Monocytes': r'\b(Monocyte)\b',
        'Basophils': r'\b(Basophil)\b',
       
        'ESR': r'\b(Erythrocyte Sedimentation Rate|ESR)\b',
        'CRP': r'\b(CRP|C-Reactive Protein)\b',
        
        'Glucose': r'\b(Glucose|Blood Sugar|FBS|Fasting Blood Sugar)\b',
        'HbA1c': r'\b(HbA1c|Hemoglobin A1c|A1C|Glycated Hemoglobin)\b',
        'Creatinine': r'\b(Creatinine|CREAT|Serum Creatinine)\b',
        'BUN': r'\b(BUN|Blood Urea Nitrogen|Urea)\b',
        'Sodium': r'\b(Sodium|Na|Serum Sodium)\b',
        'Potassium': r'\b(Potassium|K|Serum Potassium)\b',
        'Chloride': r'\b(Chloride|Cl)\b',
        'Calcium': r'\b(Calcium|Ca|Serum Calcium)\b',

        'Cholesterol': r'\b(Cholesterol|CHOL|Total Cholesterol)\b',
        'LDL': r'\b(LDL|Low Density Lipoprotein|Bad Cholesterol)\b',
        'HDL': r'\b(HDL|High Density Lipoprotein|Good Cholesterol)\b',
        'Triglycerides': r'\b(Triglyceride)\b',
        'VLDL': r'\b(VLDL|Very Low Density Lipoprotein)\b',
   
        'ALT': r'\b(ALT|SGPT|Alanine Aminotransferase)\b',
        'AST': r'\b(AST|SGOT|Aspartate Aminotransferase)\b',
        'Bilirubin': r'\b(Bilirubin|BILI|Total Bilirubin)\b',
        'ALP': r'\b(ALP|Alkaline Phosphatase)\b',
        'Albumin': r'\b(Albumin|ALB|Serum Albumin)\b',
      
        'TSH': r'\b(TSH|Thyroid Stimulating Hormone)\b',
        'T3': r'\b(T3|Triiodothyronine)\b',
        'T4': r'\b(T4|Thyroxine|Free T4)\b',
        
        'Widal Test (S.Typhi)': r'\b(S\.Typhi|Salmonella Typhi)\b',
        'Widal Test': r'\b(Widal Test|Widal)\b',
        
        'Ferritin': r'\b(Ferritin|Serum Ferritin)\b',
        'Iron': r'\b(Iron|Serum Iron|Fe)\b',
        'Vitamin D': r'\b(Vitamin D|25-OH Vitamin D|Vit D)\b',
        'Vitamin B12': r'\b(Vitamin B12|B12|Cobalamin)\b',
        'PSA': r'\b(PSA|Prostate Specific Antigen)\b',
        'Uric Acid': r'\b(Uric Acid|Urate)\b',
    }

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract all text from PDF"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            logger.info(f"Successfully extracted {len(text)} characters from PDF")
            return text
        except Exception as e:
            logger.error(f"Error extracting PDF: {e}")
            raise
    
    def extract_medical_terms(self, text: str) -> List[Dict]:
        """Extract medical terms with their values and context"""
        terms_found = []
        seen_terms = set()
        
        for term_name, pattern in self.MEDICAL_PATTERNS.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                if term_name in seen_terms:
                    continue
                
                seen_terms.add(term_name)
                
         
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end]
         
                value, unit = self._extract_value_and_unit(context)
                
                terms_found.append({
                    'term': term_name,
                    'value': value,
                    'unit': unit,
                    'context': context.strip()
                })
        
        return terms_found
    
    def _extract_value_and_unit(self, context: str) -> Tuple[str, str]:
        """Extract numeric value and unit from context"""
       
        patterns = [
            r'(\d+\.?\d*)\s*(g/dL|g/dl|gm/dl)',  
            r'(\d+\.?\d*)\s*(mm/hr|mm/h)',        
            r'(\d+\.?\d*)\s*(10\^3/uL|x10\^3/uL|10\^3/µL)', 
            r'(\d+\.?\d*)\s*(million/cumm|10\^6/µL)',  
            r'(\d+\.?\d*)\s*(Cells/cumm|cells/µL|10\^3/µL)',  
            r'(\d+\.?\d*)\s*(%)',                 
            r'(\d+\.?\d*)\s*(um\^3|fL|fl)',     
            r'(\d+\.?\d*)\s*(mg/dL|mg/dl|mmol/L)',  
            r'(\d+\.?\d*)\s*([a-zA-Z]+/[a-zA-Z]+)',  
        ]
        
        for pattern in patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                value = match.group(1)
                unit = match.group(2)
                return value, unit

        number_match = re.search(r'(\d+\.?\d*)', context)
        if number_match:
            return number_match.group(1), ""
        
        return "", ""
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""

        text = re.sub(r'\s+', ' ', text)

        text = re.sub(r'[^\w\s\.\,\:\-\(\)\/\%]', '', text)
        return text.strip()
