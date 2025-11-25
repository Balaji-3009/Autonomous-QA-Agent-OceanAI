from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import os
import shutil
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import google.generativeai as genai
from utils import extract_text_from_pdf, parse_json, parse_markdown

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_embedding(text: str) -> List[float]:
    """Get embedding using Gemini API"""
    try:
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except:
        import hashlib
        h = hashlib.sha256(text.encode()).hexdigest()
        return [float(int(h[i:i+2], 16))/255.0 for i in range(0, min(len(h), 768), 2)]

chroma_client = chromadb.Client(Settings(
    anonymized_telemetry=False,
    allow_reset=True
))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY and GEMINI_API_KEY != "dummy_key_placeholder":
    genai.configure(api_key=GEMINI_API_KEY)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

knowledge_base = None
html_content_global = ""

class TestCaseRequest(BaseModel):
    query: str = "Generate all test cases"

class ScriptRequest(BaseModel):
    test_case: str
    html_content: str

@app.post("/upload-and-build-kb")
async def upload_and_build_kb(files: List[UploadFile] = File(...)):
    """Upload files and build vector database knowledge base"""
    global knowledge_base, html_content_global
    
    try:
        try:
            chroma_client.delete_collection("qa_knowledge_base")
        except:
            pass
        
        knowledge_base = chroma_client.create_collection(
            name="qa_knowledge_base",
            metadata={"description": "QA documentation knowledge base"}
        )
        
        documents = []
        metadatas = []
        ids = []
        doc_id = 0
        
        for file in files:
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            if file.filename.endswith(".html"):
                with open(file_path, "r", encoding="utf-8") as f:
                    html_content_global = f.read()
                content = f"HTML Structure: {html_content_global[:1000]}"  
            elif file.filename.endswith(".pdf"):
                content = extract_text_from_pdf(file_path)
            elif file.filename.endswith(".md"):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            elif file.filename.endswith(".txt"):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            elif file.filename.endswith(".json"):
                content = parse_json(file_path)
            else:
                continue
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
            chunks = text_splitter.split_text(content)
            
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    documents.append(chunk)
                    metadatas.append({
                        "source_document": file.filename,
                        "chunk_index": i
                    })
                    ids.append(f"doc_{doc_id}")
                    doc_id += 1
        
        if documents:
            embeddings = [get_embedding(doc) for doc in documents]
            knowledge_base.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
        
        return {
            "status": "success",
            "message": f"Knowledge base built with {len(documents)} chunks from {len(files)} files",
            "num_chunks": len(documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-test-cases")
async def generate_test_cases(request: TestCaseRequest):
    """Generate test cases using RAG pipeline"""
    global knowledge_base
    
    if not knowledge_base:
        raise HTTPException(status_code=400, detail="Knowledge base not built. Please upload documents first.")
    
    try:
        query_embedding = get_embedding(request.query)
        results = knowledge_base.query(
            query_embeddings=[query_embedding],
            n_results=5
        )
        
        context = "\n\n".join([
            f"From {meta['source_document']}:\n{doc}"
            for doc, meta in zip(results['documents'][0], results['metadatas'][0])
        ])
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = f"""
You are a QA expert. Generate test cases based on the provided documentation.

Retrieved Context:
{context}

OUTPUT FORMAT (MUST BE JSON):
Return a JSON array of test cases. Each test case must have this structure:
{{
  "test_id": "TC-001",
  "feature": "Feature name",
  "test_scenario": "Description",
  "expected_result": "Expected outcome",
  "grounded_in": "source_document.md"
}}

Generate comprehensive test cases covering all features mentioned in the documentation.
"""
        
        response = model.generate_content(prompt)
        
        import json
        import re
        
        text = response.text
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        if json_match:
            try:
                test_cases_json = json.loads(json_match.group())
                return {"test_cases": test_cases_json}
            except:
                pass
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        test_cases = []
        current_tc = {}
        
        for line in lines:
            if line.startswith('Test_ID:') or line.startswith('test_id'):
                if current_tc:
                    test_cases.append(current_tc)
                current_tc = {"raw": line}
            elif any(skip in line.lower() for skip in ['here are', 'based on', 'following']):
                continue
            else:
                if not current_tc:
                    current_tc = {"raw": ""}
                current_tc["raw"] += " " + line
        
        if current_tc:
            test_cases.append(current_tc)
        
        if not test_cases:
            test_cases = [{"test_scenario": line, "grounded_in": "documentation"} for line in lines if len(line) > 10]
        
        return {"test_cases": test_cases}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-script")
async def generate_script(request: ScriptRequest):
    """Generate Selenium script using RAG pipeline"""
    global knowledge_base, html_content_global
    
    if not knowledge_base:
        raise HTTPException(status_code=400, detail="Knowledge base not built")
    
    try:
        query_embedding = get_embedding(request.test_case)
        results = knowledge_base.query(
            query_embeddings=[query_embedding],
            n_results=3
        )
        
        context = "\n\n".join([
            f"From {meta['source_document']}:\n{doc}"
            for doc, meta in zip(results['documents'][0], results['metadatas'][0])
        ])
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = f"""
You are a Selenium automation expert. Generate a Python Selenium script for this test case.

Test Case:
{request.test_case}

HTML Content:
{request.html_content[:2000]}

Documentation Context:
{context}

REQUIREMENTS:
1. Use exact element IDs/names from the HTML
2. Include proper imports
3. Add explicit waits where needed
4. Include assertions
5. Return ONLY the Python code, no markdown

EXAMPLE:
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()
driver.get("file:///path/to/checkout.html")  # USER MUST UPDATE THIS PATH
...
"""
        
        response = model.generate_content(prompt)
        script = response.text
        
        if "```python" in script:
            script = script.split("```python")[1].split("```")[0]
        elif "```" in script:
            script = script.split("```")[1].split("```")[0]
        
        return {"script": script.strip()}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "QA Agent Backend Running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
