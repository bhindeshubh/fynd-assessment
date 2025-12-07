import streamlit as st

# Page configuration
st.set_page_config(
    page_title="AI Feedback System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .feature-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        height: 60px;
        font-size: 1.2rem;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""<div class="main-header">🤖 Shubh's AI Feedback System</div>""", unsafe_allow_html=True)
st.markdown('<div class="sub-header">Intelligent Review Management Platform</div>', unsafe_allow_html=True)

st.markdown("---")

# Introduction
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    ### Welcome to the AI Feedback System
    
    This application provides two powerful dashboards for managing customer reviews:
    
    - **👤 User Dashboard**: Submit reviews and receive AI-generated responses
    - **👨‍💼 Admin Dashboard**: View all submissions, analytics, and recommended actions
    
    Built with Streamlit and powered by OpenRouter.
    """)

st.markdown("---")

# Dashboard Selection
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-box">
        <h3>👤 User Dashboard</h3>
        <p><strong>For Customers:</strong></p>
        <ul>
            <li>Submit star ratings (1-5)</li>
            <li>Write detailed reviews</li>
            <li>Get instant AI-generated responses</li>
            <li>Receive acknowledgment and suggestions</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # if st.button("📝 Go to User Dashboard", key="user_btn", use_container_width=True):
    #     st.switch_page("pages/1_User_Dashboard.py")

with col2:
    st.markdown("""
    <div class="feature-box">
        <h3>👨‍💼 Admin Dashboard</h3>
        <p><strong>For Management:</strong></p>
        <ul>
            <li>View all customer submissions</li>
            <li>AI-generated summaries</li>
            <li>Recommended action items</li>
            <li>Analytics and insights</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # if st.button("📊 Go to Admin Dashboard", key="admin_btn", use_container_width=True):
    #     st.switch_page("pages/2_Admin_Dashboard.py")

st.markdown("---")

# Features Section
st.markdown("### ✨ Key Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    #### 🤖 AI-Powered
    - Intelligent response generation
    - Automatic summarization
    - Action recommendations
    """)

with col2:
    st.markdown("""
    #### 📊 Real-Time Analytics
    - Live submission tracking
    - Rating distribution
    - Sentiment analysis
    """)

with col3:
    st.markdown("""
    #### 💾 Persistent Storage
    - SQLite database
    - Searchable history
    - Export capabilities
    """)

st.markdown("---")

# Footer
st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem 0;">
        <p>Built for Fynd AI Engineer Intern Assignment</p>
        <p>Powered by OpenRouter | Streamlit Framework</p>
    </div>
""", unsafe_allow_html=True)
