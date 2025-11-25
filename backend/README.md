# QA Agent Backend - FastAPI

AI-powered QA Agent backend with RAG pipeline for test case and Selenium script generation.

## Features

- ✅ FastAPI REST API
- ✅ RAG Pipeline with ChromaDB vector database
- ✅ Gemini AI integration for test generation
- ✅ Document processing (PDF, MD, TXT, JSON, HTML)
- ✅ Test case generation from documentation
- ✅ Automated Selenium script generation

## Tech Stack

- **Framework**: FastAPI
- **AI**: Google Gemini (gemini-2.0-flash-exp)
- **Vector DB**: ChromaDB
- **Embeddings**: Gemini Embeddings API
- **Text Processing**: LangChain

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
```

### 3. Run Locally

```bash
uvicorn main:app --reload
```

Server runs at: http://localhost:8000

## API Endpoints

### `GET /`
Health check endpoint

**Response:**
```json
{"message": "QA Agent Backend Running"}
```

### `POST /upload-and-build-kb`
Upload documents and build knowledge base

**Request:** Multipart form with files
**Response:** Success message with chunk count

### `POST /generate-test-cases`
Generate test cases using RAG pipeline

**Request:**
```json
{"query": "Generate comprehensive test cases"}
```

**Response:**
```json
{"test_cases": [...]}
```

### `POST /generate-script`
Generate Selenium script for test case

**Request:**
```json
{
  "test_case": "Test case description",
  "html_content": "<html>...</html>"
}
```

**Response:**
```json
{"script": "Python Selenium code..."}
```

## Deployment

Deployed on Render.com

### Environment Variables Required:
- `GEMINI_API_KEY`: Your Google Gemini API key
- `PORT`: Auto-set by Render

## License

MIT
