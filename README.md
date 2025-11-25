# Autonomous QA Agent for Test Case and Script Generation

An intelligent system that generates test cases and Selenium scripts from project documentation.

## Features

- **Document Ingestion**: Upload HTML files and support documents (MD, TXT, JSON, PDF)
- **Knowledge Base**: Builds a searchable knowledge base from your documentation
- **Test Case Generation**: AI-powered test case creation grounded in provided documents
- **Selenium Script Generation**: Automatic conversion of test cases to executable Python code
- **No Hallucinations**: All outputs strictly based on uploaded documentation

## Tech Stack

- **Backend**: FastAPI
- **Frontend**: Streamlit
- **AI**: Google Gemini (gemini-2.0-flash)
- **Testing**: Selenium WebDriver

## Prerequisites

- Python 3.8 or higher
- Google Gemini API Key

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Create/Edit `.env` file in the `backend` directory:
```
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Run the Backend

```bash
cd backend
uvicorn main:app --reload
```

The backend will run at `http://localhost:8000`

### 4. Run the Frontend

Open a new terminal:
```bash
streamlit run app.py
```

The Streamlit UI will open in your browser (usually `http://localhost:8501`)

## Usage Guide

### Step 1: Prepare Your Assets

Ensure you have:
- 1 HTML file (e.g., `checkout.html`)
- 3-5 support documents:
  - `product_specs.md` - Feature specifications
  - `ui_ux_guide.txt` - UI/UX guidelines
  - `api_endpoints.json` - API documentation

Sample files are provided in the `assets/` folder.

### Step 2: Upload Documents

1. Open the Streamlit app in your browser
2. Use the sidebar to upload:
   - Your HTML file
   - Support documents (MD, TXT, JSON, PDF)
3. Click "Build Knowledge Base"

### Step 3: Generate Test Cases

- The system will analyze your documents
- Test cases will appear in the "Test Cases" tab
- All test cases are grounded in your uploaded documentation

### Step 4: Generate Selenium Scripts

1. Select a test case from the list
2. Navigate to the "Generate Script" tab
3. Click "Generate Selenium Script"
4. Copy the generated Python code
5. Run it locally or integrate into your test suite

## Project Structure

```
.
├── app.py                  # Streamlit frontend
├── backend/
│   ├── main.py            # FastAPI backend
│   ├── ai_service.py      # Gemini AI integration
│   ├── utils.py           # Helper functions
│   ├── requirements.txt   # Backend dependencies
│   └── .env               # API keys (not committed)
├── assets/
│   ├── checkout.html      # Target HTML file
│   ├── product_specs.md   # Product specifications
│   ├── ui_ux_guide.txt    # UI/UX guidelines
│   └── api_endpoints.json # API documentation
├── requirements.txt       # Root project dependencies
└── README.md              # This file
```

## Example Test Case Output

```
Test Case: Verify discount code SAVE15 applies 15% discount
Grounded In: product_specs.md
Expected Result: Cart total reduced by 15%
```

## Example Generated Script

```python
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("file:///path/to/checkout.html")

# Apply discount code
driver.find_element(By.ID, "discount-code").send_keys("SAVE15")
driver.find_element(By.ID, "apply-discount").click()

# Verify discount applied
assert "15% discount applied" in driver.page_source

driver.quit()
```

## Support Documents Explained

### 1. product_specs.md
Contains feature rules and business logic:
- Discount code behavior
- Shipping costs
- Product pricing

### 2. ui_ux_guide.txt
Defines UI/UX requirements:
- Error message styling (red text)
- Button colors (green for Pay Now)
- Form validation behavior

### 3. api_endpoints.json
Documents API structure:
- Available endpoints
- Request/response formats
- Validation rules

## Important Notes

- Ensure backend is running before starting Streamlit
- Replace the dummy API key in `.env` with your actual key
- Test cases are generated based ONLY on provided documents
- Scripts use actual element IDs from your HTML

## Contributing

This project was built as part of an assignment for Ocean AI.

## 📧 Support

For issues or questions, please check:
- Backend is running at `http://localhost:8000`
- Streamlit is running at `http://localhost:8501`
- API key is correctly configured in `.env`
