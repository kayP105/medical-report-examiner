# Medical Report Explainer

A full-stack web application that allows users to upload their medical reports (PDFs) and receive easy-to-understand explanations, a summary of key findings, and interact via chat to ask questions about specific tests and results.

---

## Features

- Upload medical report PDFs and extract key test results automatically.
- Provide clear, simple explanations of medical terms and findings.
- Interactive chat capability powered by Google Gemini API for in-depth Q&A.
- Reference range verification with gender-aware value analysis.
- Rich frontend built with React, responsive and user-friendly.
- Backend implemented with FastAPI, including knowledge base retrieval and OpenAI Gemini integration.

---

## Technology Stack

- **Frontend:** React, Axios, React Icons
- **Backend:** FastAPI, LangChain, FAISS vector store
- **AI:** Google Gemini API (chat and generation)
- **PDF Processing:** pdfplumber
- **Data Storage:** Local JSON/text vector DB
- **Version Control:** Git + GitHub

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Google Gemini API Key (placed in `.env` as `OPENAI_API_KEY`)
- Recommended: Create a virtual environment for Python dependencies.

### Installation

#### Backend

