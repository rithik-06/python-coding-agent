"""
Python Debug Agent - Streamlit Web Interface
"""

import streamlit as st
import tempfile
import os
from pathlib import Path
import subprocess
import sys

# Set page config
st.set_page_config(
    page_title="Python Debug Agent",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #667eea;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #764ba2;
    }
    .success-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🐍 Python Debug Agent</h1>
    <p>AI-Powered Code Debugging & Fixing</p>
    <p style="font-size: 0.9rem; opacity: 0.9;">Upload buggy code • Get instant fixes • Download corrected version</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        help="Get your free API key from https://makersuite.google.com/app/apikey"
    )
    
    if not api_key:
        st.warning("⚠️ Please enter your Gemini API key to use the agent")
        st.markdown("""
        **How to get API key:**
        1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. Click 'Create API Key'
        3. Copy and paste it here
        
        It's completely free!
        """)
    
    st.divider()
    
    st.header("📊 Stats")
    if "fixes_count" not in st.session_state:
        st.session_state.fixes_count = 0
    st.metric("Fixes Generated", st.session_state.fixes_count)
    
    st.divider()
    
    st.header("ℹ️ About")
    st.markdown("""
    This AI agent:
    - Detects Python errors
    - Generates fixes automatically
    - Explains the issues
    - Tests the fixed code
    
    Powered by Google Gemini
    """)

# Main content
tab1, tab2, tab3 = st.tabs(["📁 Upload File", "✍️ Paste Code", "📚 Examples"])

with tab1:
    st.header("Upload Python File")
    
    uploaded_file = st.file_uploader(
        "Choose a Python file",
        type=['py'],
        help="Upload a .py file with bugs"
    )
    
    if uploaded_file:
        code = uploaded_file.read().decode('utf-8')
        st.code(code, language='python', line_numbers=True)
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🔧 Fix Code", key="fix_upload"):
                if not api_key:
                    st.error("Please enter your API key in the sidebar")
                else:
                    with st.spinner("AI is analyzing your code..."):
                        result = fix_code(code, api_key)
                        st.session_state.result = result
                        st.session_state.original_code = code
                        st.session_state.fixes_count += 1
                        st.rerun()

with tab2:
    st.header("Paste Your Code")
    
    code_input = st.text_area(
        "Enter Python code here",
        height=300,
        placeholder="# Paste your buggy Python code here\nprint(undefined_variable)",
        help="Type or paste your Python code"
    )
    
    if code_input:
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🔧 Fix Code", key="fix_paste"):
                if not api_key:
                    st.error("Please enter your API key in the sidebar")
                else:
                    with st.spinner("AI is analyzing your code..."):
                        result = fix_code(code_input, api_key)
                        st.session_state.result = result
                        st.session_state.original_code = code_input
                        st.session_state.fixes_count += 1
                        st.rerun()

with tab3:
    st.header("Try Example Codes")
    
    examples = {
        "Undefined Variable": "print(undefined_variable)",
        "Division by Zero": "def divide(a, b):\n    return a / b\n\nprint(divide(10, 0))",
        "Index Error": "my_list = [1, 2, 3]\nprint(my_list[10])",
        "Type Error": "result = '5' + 5\nprint(result)",
    }
    
    selected_example = st.selectbox("Choose an example", list(examples.keys()))
    
    st.code(examples[selected_example], language='python')
    
    if st.button("🔧 Fix This Example"):
        if not api_key:
            st.error("Please enter your API key in the sidebar")
        else:
            with st.spinner("AI is analyzing..."):
                result = fix_code(examples[selected_example], api_key)
                st.session_state.result = result
                st.session_state.original_code = examples[selected_example]
                st.session_state.fixes_count += 1
                st.rerun()

# Display results
if "result" in st.session_state:
    st.divider()
    st.header("📊 Results")
    
    result = st.session_state.result
    
    # Error detection
    if result["has_error"]:
        st.markdown(f"""
        <div class="error-box">
            <strong>❌ Error Detected:</strong><br>
            <code>{result['error_type']}: {result['error_message']}</code>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="success-box">
            <strong>✅ No errors detected!</strong> Your code runs successfully.
        </div>
        """, unsafe_allow_html=True)
    
    # Show comparison
    if result["has_error"] and result["fixed_code"]:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔴 Original Code")
            st.code(st.session_state.original_code, language='python', line_numbers=True)
        
        with col2:
            st.subheader("✅ Fixed Code")
            st.code(result["fixed_code"], language='python', line_numbers=True)
        
        # Explanation
        if result.get("explanation"):
            st.subheader("💡 What Changed")
            st.info(result["explanation"])
        
        # Download button
        st.download_button(
            label="💾 Download Fixed Code",
            data=result["fixed_code"],
            file_name="fixed_code.py",
            mime="text/plain"
        )


def execute_code(code):
    """Execute Python code and capture output/errors"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        os.unlink(temp_file)
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Execution timeout"
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e)
        }


def fix_code(code, api_key):
    """Fix code using Gemini API"""
    import google.generativeai as genai
    
    # Execute original code
    exec_result = execute_code(code)
    
    if exec_result["success"]:
        return {
            "has_error": False,
            "fixed_code": code,
            "error_type": None,
            "error_message": None
        }
    
    # Parse error
    stderr = exec_result["stderr"]
    lines = stderr.strip().split('\n')
    error_type = "Unknown"
    error_message = stderr
    
    for line in reversed(lines):
        if ':' in line and any(err in line for err in ['Error', 'Exception']):
            parts = line.split(':', 1)
            error_type = parts[0].strip()
            error_message = parts[1].strip() if len(parts) > 1 else ""
            break
    
    # Use Gemini to fix
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""Fix this Python code. The code has an error.

Code:
```python
{code}
```

Error:
{stderr}

Provide:
1. The corrected Python code (wrapped in ```python code blocks)
2. A brief explanation of what was wrong and how you fixed it

Format your response as:
FIXED CODE:
```python
# corrected code here
```

EXPLANATION:
Brief explanation here
"""
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Extract fixed code
        fixed_code = code  # fallback
        if "```python" in response_text:
            start = response_text.find("```python") + 9
            end = response_text.find("```", start)
            if end != -1:
                fixed_code = response_text[start:end].strip()
        
        # Extract explanation
        explanation = ""
        if "EXPLANATION:" in response_text:
            explanation = response_text.split("EXPLANATION:")[1].strip()
        
        # Verify fix
        verify_result = execute_code(fixed_code)
        
        return {
            "has_error": True,
            "fixed_code": fixed_code,
            "error_type": error_type,
            "error_message": error_message,
            "explanation": explanation,
            "fix_verified": verify_result["success"]
        }
    
    except Exception as e:
        st.error(f"Error using Gemini API: {e}")
        return {
            "has_error": True,
            "fixed_code": None,
            "error_type": error_type,
            "error_message": error_message,
            "explanation": f"Failed to generate fix: {str(e)}"
        }


# Footer
st.divider()
st.markdown("""
<div style="text-align: center; opacity: 0.7; padding: 1rem;">
    Made with ❤️ using Streamlit and Google Gemini | 
    <a href="https://github.com/yourusername/python-debug-agent">GitHub</a>
</div>
""", unsafe_allow_html=True)