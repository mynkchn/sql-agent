import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:5000"

# Page configuration
st.set_page_config(
    page_title="SQL Agent - VMC Database",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern minimalist CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background-color: #0f1419;
        color: #e7e9ea;
        padding: 2rem 3rem;
    }
    
    .stApp {
        background-color: #0f1419;
    }
    
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 0 2rem 0;
        border-bottom: 1px solid #2f3336;
        margin-bottom: 3rem;
    }
    
    .main-title {
        font-size: 2rem;
        font-weight: 600;
        color: #e7e9ea;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .status-indicator {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        background-color: #16181c;
        padding: 0.6rem 1.2rem;
        border-radius: 24px;
        border: 1px solid #2f3336;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #00ba7c;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .status-dot-offline {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #f4212e;
    }
    
    .status-text {
        font-size: 0.875rem;
        color: #71767b;
        font-weight: 500;
    }
    
    .intro-box {
        background: linear-gradient(135deg, #1a1f2e 0%, #16181c 100%);
        border: 1px solid #2f3336;
        border-radius: 12px;
        padding: 2.5rem;
        margin-bottom: 3rem;
    }
    
    .feature-box {
        background-color: #16181c;
        border: 1px solid #2f3336;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .feature-box:hover {
        border-color: #1d9bf0;
        transform: translateY(-2px);
    }
    
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin-bottom: 3rem;
    }
    
    .stat-card {
        background-color: #16181c;
        border: 1px solid #2f3336;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .stat-label {
        font-size: 0.75rem;
        color: #71767b;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #e7e9ea;
    }
    
    .query-section {
        background-color: #16181c;
        border: 1px solid #2f3336;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 2rem;
    }
    
    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #e7e9ea;
        margin-bottom: 1.5rem;
    }
    
    .table-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 0.75rem;
        margin: 1.5rem 0;
    }
    
    .table-badge {
        background-color: #1a1f2e;
        border: 1px solid #2f3336;
        color: #8b949e;
        padding: 0.75rem;
        border-radius: 8px;
        text-align: center;
        font-size: 0.875rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .table-badge:hover {
        border-color: #1d9bf0;
        color: #1d9bf0;
    }
    
    .result-success {
        background-color: #0d3a2e;
        border: 1px solid #00ba7c;
        border-radius: 10px;
        padding: 1.5rem;
        margin-top: 2rem;
    }
    
    .result-error {
        background-color: #3a0d0d;
        border: 1px solid #f4212e;
        border-radius: 10px;
        padding: 1.5rem;
        margin-top: 2rem;
    }
    
    .stTextArea textarea {
        background-color: #1a1f2e !important;
        border: 1px solid #2f3336 !important;
        color: #e7e9ea !important;
        border-radius: 8px !important;
        font-size: 0.95rem !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #1d9bf0 !important;
        box-shadow: 0 0 0 1px #1d9bf0 !important;
    }
    
    .stButton button {
        background-color: #1d9bf0 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton button:hover {
        background-color: #1a8cd8 !important;
        transform: translateY(-1px);
    }
    
    div[data-testid="stDataFrame"] {
        background-color: #16181c;
        border: 1px solid #2f3336;
        border-radius: 8px;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    </style>
""", unsafe_allow_html=True)

# Helper functions
def get_agent_info():
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code == 200:
            return response.json(), None
        return None, f"Status code: {response.status_code}"
    except Exception as e:
        return None, str(e)

def get_database_info():
    try:
        response = requests.get(f"{API_BASE_URL}/database", timeout=5)
        if response.status_code == 200:
            return response.json(), None
        return None, f"Status code: {response.status_code}"
    except Exception as e:
        return None, str(e)

def ask_question(question):
    try:
        response = requests.post(
            f"{API_BASE_URL}/ask",
            params={"question": question},
            timeout=60
        )
        if response.status_code == 200:
            return response.json(), None
        return None, f"Status code: {response.status_code}"
    except requests.exceptions.Timeout:
        return None, "Request timed out"
    except Exception as e:
        return None, str(e)

# Initialize session state
if 'show_intro' not in st.session_state:
    st.session_state.show_intro = True

# Check agent status
agent_info, agent_error = get_agent_info()
is_online = agent_info is not None

# Header
header_html = f"""
<div class="header-container">
    <div class="main-title">SQL Agent Interface</div>
    <div class="status-indicator">
        <div class="{'status-dot' if is_online else 'status-dot-offline'}"></div>
        <span class="status-text">{'System Online' if is_online else 'System Offline'}</span>
    </div>
</div>
"""
# st.markdown(header_html, unsafe_allow_html=True)

# Introduction Section
if st.session_state.show_intro:
    st.markdown('<div class="intro-box">', unsafe_allow_html=True)
    
    st.markdown("## Welcome to VMC AI Civic Issue Management System")
    
    st.markdown("""
    This SQL Agent is built using LangChain to communicate with the Vadodara Municipal Corporation AI Civic Issue Management Database. 
    Instead of searching through long lists and multiple tables, simply ask questions in natural language and get instant answers. 
    The agent understands your queries, translates them to SQL, executes them on the database, and presents results in an easy-to-understand format.
    """)
    
    
    
    # Feature cards using columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="feature-box">', unsafe_allow_html=True)
        st.markdown("#### Natural Language Queries")
        st.markdown("Ask questions in plain English without writing any SQL code. The agent translates your intent into optimized database queries.")
       
        st.markdown('<div class="feature-box">', unsafe_allow_html=True)
        st.markdown("#### Smart Context Understanding")
        st.markdown("Powered by LangChain, the agent understands database schema, relationships, and context to provide accurate and relevant results.")
       
    
    with col2:
        st.markdown('<div class="feature-box">', unsafe_allow_html=True)
        st.markdown("#### Instant Data Retrieval")
        st.markdown("Get immediate answers to complex questions that would otherwise require navigating through multiple database tables and relationships.")
        
        
        st.markdown('<div class="feature-box">', unsafe_allow_html=True)
        st.markdown("#### Civic Issue Management")
        st.markdown("Access information about issues, assignments, resolutions, routes, wards, and survey data across Vadodara Municipal Corporation.")
        
    
    st.markdown("")
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("Get Started", use_container_width=True):
            st.session_state.show_intro = False
            st.rerun()

if not st.session_state.show_intro:
    # Database Statistics
    db_info, db_error = get_database_info()
    
    if db_info:
        tables = db_info.get('Tables', [])
        
        stats_html = f"""
        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-label">Database Engine</div>
                <div class="stat-value">PostgreSQL</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Tables</div>
                <div class="stat-value">{len(tables)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Agent Status</div>
                <div class="stat-value">Active</div>
            </div>
        </div>
        """
        st.markdown(stats_html, unsafe_allow_html=True)
        
        # Database Tables
        st.markdown('<div class="query-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Available Tables</div>', unsafe_allow_html=True)
        
        if tables:
            table_html = '<div class="table-grid">'
            for table in tables:
                table_html += f'<div class="table-badge">{table}</div>'
            table_html += '</div>'
            st.markdown(table_html, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Query Interface
    st.markdown('<div class="query-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Ask a Question</div>', unsafe_allow_html=True)
    
    # Query Input
    question = st.text_area(
        "",
        height=120,
        placeholder="Example: How many civic issues were reported in the last month?\nExample: Show me all pending issue assignments\nExample: Which ward has the most resolved issues?",
        key="query_input",
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([1, 1, 4])
    
    with col1:
        execute_btn = st.button("Execute Query", type="primary", use_container_width=True)
    
    with col2:
        clear_btn = st.button("Clear", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Execute Query
    if execute_btn and question:
        if not is_online:
            error_html = """
            <div class="result-error">
                <div style="font-size: 1rem; font-weight: 600; color: #e7e9ea; margin-bottom: 1rem;">System Offline</div>
                <p style="color: #8b949e; margin: 0;">The SQL Agent API is not responding. Please ensure the FastAPI server is running on localhost:5000</p>
            </div>
            """
            st.markdown(error_html, unsafe_allow_html=True)
        else:
            with st.spinner("Processing your query..."):
                result, error = ask_question(question)
                
                if result:
                    st.markdown('<div class="result-success">', unsafe_allow_html=True)
                    st.markdown('<div style="font-size: 1rem; font-weight: 600; color: #e7e9ea; margin-bottom: 1rem;">Query Results</div>', unsafe_allow_html=True)
                    
                    # Display result
                    if isinstance(result, dict):
                        if 'content' in result:
                            st.markdown(f"<p style='color: #8b949e;'>{result['content']}</p>", unsafe_allow_html=True)
                        else:
                            st.json(result)
                    elif isinstance(result, list):
                        try:
                            df = pd.DataFrame(result)
                            st.dataframe(df, use_container_width=True)
                        except:
                            st.write(result)
                    else:
                        st.write(result)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    error_html = f"""
                    <div class="result-error">
                        <div style="font-size: 1rem; font-weight: 600; color: #e7e9ea; margin-bottom: 1rem;">Query Failed</div>
                        <p style="color: #8b949e; margin: 0;">{error}</p>
                    </div>
                    """
                    st.markdown(error_html, unsafe_allow_html=True)
    
    if clear_btn:
        st.rerun()
    
    # Show intro toggle
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Introduction"):
        st.session_state.show_intro = True
        st.rerun()

# Footer
footer_html = """
<div style='text-align: center; color: #71767b; padding: 2rem 0 1rem 0; border-top: 1px solid #2f3336; margin-top: 3rem;'>
    <p style='margin: 0; font-size: 0.875rem;'>SQL Agent Interface | Vadodara Municipal Corporation</p>
    <p style='margin: 0.5rem 0 0 0; font-size: 0.75rem;'>Powered by LangChain and FastAPI</p>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)