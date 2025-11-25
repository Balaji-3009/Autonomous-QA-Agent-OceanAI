import pypdf
from bs4 import BeautifulSoup
import json

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF with robust error handling"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            
            if reader.is_encrypted:
                return "Error: PDF is encrypted"
            
            max_pages = min(len(reader.pages), 50)
            for i in range(max_pages):
                try:
                    page_text = reader.pages[i].extract_text()
                    if page_text:
                        text += page_text + "\n"
                except Exception as e:
                    continue
                    
    except Exception as e:
        return f"Error reading PDF: {str(e)}"
    
    return text if text else "No text found in PDF"

def parse_json(file_path: str) -> str:
    """Parse JSON file and convert to readable text"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"Error parsing JSON: {str(e)}"

def parse_markdown(file_path: str) -> str:
    """Read markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading markdown: {str(e)}"
