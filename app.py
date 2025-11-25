import streamlit as st
import requests
import json

st.set_page_config(
    page_title="Autonomous QA Agent",
    layout="wide"
)

API_URL = "http://localhost:8000"

if 'kb_built' not in st.session_state:
    st.session_state.kb_built = False
if 'test_cases' not in st.session_state:
    st.session_state.test_cases = []
if 'selected_test_case' not in st.session_state:
    st.session_state.selected_test_case = None
if 'generated_script' not in st.session_state:
    st.session_state.generated_script = None
if 'auto_generate_script' not in st.session_state:
    st.session_state.auto_generate_script = False
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0
if 'html_content' not in st.session_state:
    st.session_state.html_content = ""
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []

st.title("Autonomous QA Agent")
st.markdown("### Test Case & Selenium Script Generator with RAG Pipeline")

with st.sidebar:
    st.header("Phase 1: Knowledge Base Ingestion")
    
    st.info("Upload your project documentation to build the knowledge base")
    
    html_file = st.file_uploader(
        "Upload checkout.html *",
        type=['html'],
        help="The target HTML file to test"
    )
    
    support_docs = st.file_uploader(
        "Upload Support Documents (3-5 files) *",
        type=['md', 'txt', 'json', 'pdf'],
        accept_multiple_files=True,
        help="Product specs, UI/UX guidelines, API docs, etc."
    )
    
    if support_docs:
        doc_count = len(support_docs)
        if doc_count < 3:
            st.warning(f"{doc_count} document(s) uploaded. Recommended: 3-5 documents for better results")
        elif doc_count > 5:
            st.info(f"ℹ{doc_count} documents uploaded. Recommended: 3-5 documents")
        else:
            st.success(f"{doc_count} documents uploaded (recommended range)")
    else:
        st.info("Please upload support documents (recommended: 3-5 files)")
    
    st.markdown("---")
    
    if st.button("Build Knowledge Base", type="primary", use_container_width=True):
        if not html_file:
            st.error("Please upload the HTML file!")
        elif not support_docs:
            st.error("Please upload at least 1 support document!")
        else:
            with st.spinner("Building Vector Database Knowledge Base..."):
                files_to_upload = []
                files_to_upload.append(('files', (html_file.name, html_file.getvalue(), 'text/html')))
                st.session_state.html_content = html_file.getvalue().decode('utf-8')
                
                for doc in support_docs:
                    files_to_upload.append(('files', (doc.name, doc.getvalue(), doc.type)))
                
                filenames = [html_file.name] + [doc.name for doc in support_docs]
                st.session_state.uploaded_files = filenames
                
                try:
                    response = requests.post(f"{API_URL}/upload-and-build-kb", files=files_to_upload)
                    data = response.json()
                    
                    st.session_state.kb_built = True
                    st.success(f"{data['message']}")
                    st.info(f"Vector DB: {data['num_chunks']} document chunks indexed")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    if st.session_state.kb_built:
        st.success("Knowledge Base Active")
        with st.expander("Uploaded Files"):
            for file in st.session_state.uploaded_files:
                st.write(f"• {file}")

if not st.session_state.kb_built:
    st.info("**Start Here:** Upload documents in the sidebar and build the knowledge base")
    
    with st.expander("How to Use This Tool"):
        st.markdown("""
        ### Step-by-Step Guide:
        
        **Phase 1: Knowledge Base Ingestion**
        1. Upload your `checkout.html` file
        2. Upload 3-5 support documents (MD, TXT, JSON, PDF)
        3. Click "Build Knowledge Base"
        
        **Phase 2: Test Case Generation**
        - AI generates test cases using RAG (Retrieval Augmented Generation)
        - All test cases are grounded in your uploaded documents
        
        **Phase 3: Script Generation**
        - Select a test case
        - AI generates executable Selenium Python scripts
        - Scripts use actual element IDs from your HTML
        """)
else:
    if st.session_state.auto_generate_script:
        st.components.v1.html(
            """
            <script>
                // Wait for page to load, then click the second tab
                window.parent.document.addEventListener('DOMContentLoaded', (event) => {
                    setTimeout(function() {
                        const tabs = window.parent.document.querySelectorAll('[data-baseweb="tab"]');
                        if (tabs.length >= 2) {
                            tabs[1].click();
                        }
                    }, 100);
                });
                // Also try immediately in case DOM is already loaded
                setTimeout(function() {
                    const tabs = window.parent.document.querySelectorAll('[data-baseweb="tab"]');
                    if (tabs.length >= 2) {
                        tabs[1].click();
                    }
                }, 100);
            </script>
            """,
            height=0,
        )
    
    tab1, tab2, tab3 = st.tabs([
        "Phase 2: Generate Test Cases",
        "Phase 3: Generate Selenium Script",
        "About"
    ])
    
    with tab1:
        st.header("Test Case Generation (RAG Pipeline)")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("The system will retrieve relevant information from the vector database and generate test cases.")
        with col2:
            if st.button("Generate Test Cases", type="primary", use_container_width=True):
                with st.spinner("Using RAG pipeline to generate test cases..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/generate-test-cases",
                            json={"query": "Generate comprehensive test cases for all features"}
                        )
                        data = response.json()
                        st.session_state.test_cases = data['test_cases']
                        st.success(f"Generated {len(st.session_state.test_cases)} test cases!")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        st.markdown("---")
        
        if st.session_state.test_cases:
            st.subheader(f"{len(st.session_state.test_cases)} Test Cases Generated")
            
            for i, tc in enumerate(st.session_state.test_cases, 1):
                with st.container():
                    col1, col2 = st.columns([5, 1])
                    
                    with col1:
                        if isinstance(tc, dict):
                            if 'test_scenario' in tc:
                                st.markdown(f"**TC-{i:03d}:** {tc.get('test_scenario', 'N/A')}")
                            elif 'raw' in tc:
                                st.markdown(f"**{tc['raw']}**")
                            else:
                                st.markdown(f"**{str(tc)}**")
                            
                            if 'grounded_in' in tc:
                                st.caption(f"Source: {tc['grounded_in']}")
                        else:
                            st.markdown(f"**TC-{i:03d}:** {tc}")
                    
                    with col2:
                        if st.button("Generate Script", key=f"gen_{i}", use_container_width=True):
                            st.session_state.selected_test_case = tc
                            st.session_state.generated_script = None  
                            st.session_state.auto_generate_script = True  
                            st.session_state.active_tab = 1  
                            st.rerun()
                    
                    st.divider()
        else:
            st.info("Click 'Generate Test Cases' to start")
    
    with tab2:
        st.header("Selenium Script Generation")
        
        if st.session_state.auto_generate_script and st.session_state.selected_test_case and not st.session_state.generated_script:
            with st.spinner("Generating Selenium script using RAG..."):
                try:
                    test_case_str = str(st.session_state.selected_test_case)
                    response = requests.post(
                        f"{API_URL}/generate-script",
                        json={
                            "test_case": test_case_str,
                            "html_content": st.session_state.html_content
                        }
                    )
                    data = response.json()
                    st.session_state.generated_script = data['script']
                    st.session_state.auto_generate_script = False
                    st.success("Script Generated!")
                except Exception as e:
                    st.session_state.auto_generate_script = False  
                    st.error(f"Error: {str(e)}")
        
        if st.session_state.selected_test_case:
            st.success("Test Case Selected")
            
            with st.container():
                st.subheader("Selected Test Case:")
                tc = st.session_state.selected_test_case
                if isinstance(tc, dict):
                    if 'test_scenario' in tc:
                        st.info(tc.get('test_scenario', str(tc)))
                    else:
                        st.info(str(tc))
                else:
                    st.info(str(tc))
            
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("Generate Script", type="primary", use_container_width=True):
                    with st.spinner("Generating Selenium script using RAG..."):
                        try:
                            test_case_str = str(st.session_state.selected_test_case)
                            response = requests.post(
                                f"{API_URL}/generate-script",
                                json={
                                    "test_case": test_case_str,
                                    "html_content": st.session_state.html_content
                                }
                            )
                            data = response.json()
                            st.session_state.generated_script = data['script']
                            st.success("Script Generated!")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            
            if st.session_state.generated_script:
                st.markdown("---")
                st.subheader("Generated Selenium Script")
                st.code(st.session_state.generated_script, language='python', line_numbers=True)
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.download_button(
                        "Download Script",
                        st.session_state.generated_script,
                        file_name="test_script.py",
                        mime="text/x-python",
                        use_container_width=True
                    ):
                        st.success("Downloaded!")
                with col2:
                    escaped_script = st.session_state.generated_script.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
                    copy_script = f"""
                    <script>
                    function copyToClipboard() {{
                        const code = `{escaped_script}`;
                        navigator.clipboard.writeText(code).then(function() {{
                            alert('Code copied to clipboard!');
                        }}, function(err) {{
                            alert('Failed to copy code');
                        }});
                    }}
                    </script>
                    <button onclick="copyToClipboard()" style="
                        background-color: #262730;
                        color: white;
                        border: 1px solid #4e4e56;
                        border-radius: 5px;
                        padding: 10px 20px;
                        width: 100%;
                        cursor: pointer;
                        font-size: 14px;
                        font-family: 'Source Sans Pro', sans-serif;
                    ">
                        Copy to Clipboard
                    </button>
                    """
                    st.components.v1.html(copy_script, height=50)
        else:
            st.info("Go to 'Generate Test Cases' tab and select a test case first")
    
    with tab3:
        st.header("About This System")
        
        st.markdown("""
        ### 🎯 Autonomous QA Agent Features
        
        **Phase 1: Knowledge Base Ingestion**
        - ✅ Upload multiple document types (HTML, MD, TXT, JSON, PDF)
        - ✅ Text extraction and parsing
        - ✅ **Document chunking** using RecursiveCharacterTextSplitter
        - ✅ **Vector embeddings** with Sentence Transformers
        - ✅ **Chroma Vector Database** for semantic search
        - ✅ Metadata preservation (source document tracking)
        
        **Phase 2: Test Case Generation**
        - ✅ **RAG Pipeline**: Retrieve relevant docs from vector DB
        - ✅ Context-aware test case generation
        - ✅ **Grounded in documentation** (no hallucinations)
        - ✅ Structured output format
        
        **Phase 3: Selenium Script Generation**
        - ✅ **RAG-based** script generation
        - ✅ Uses actual HTML element IDs
        - ✅ Executable Python code
        - ✅ Proper imports and error handling
        
        ### 🛠️ Technology Stack
        - **Backend**: FastAPI
        - **Frontend**: Streamlit
        - **Vector DB**: ChromaDB
        - **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
        - **LLM**: Google Gemini (gemini-2.0-flash)
        - **Testing**: Selenium WebDriver
        
        ###  Support Documents
        This system uses:
        - `checkout.html` - Target web application
        - `product_specs.md` - Feature specifications
        - `ui_ux_guide.txt` - UI/UX guidelines
        - `api_endpoints.json` - API documentation
        """)

st.markdown("---")
st.caption("Autonomous QA Agent | RAG-Powered Test Generation")
