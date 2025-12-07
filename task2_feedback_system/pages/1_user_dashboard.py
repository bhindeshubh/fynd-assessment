import streamlit as st
import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_database
from utils.llm_handler import get_llm_handler

# Page configuration
st.set_page_config(
    page_title="User Dashboard - Submit Review",
    page_icon="👤",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .response-box {
        background-color: #f0f2f6;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .star-rating {
        font-size: 2rem;
        color: #ffc107;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'response_data' not in st.session_state:
    st.session_state.response_data = None

# Header
st.markdown('<div class="main-title">👤 User Dashboard</div>', unsafe_allow_html=True)
st.markdown("### Share your experience with us!")

st.markdown("---")

# Main form
if not st.session_state.submitted:
    with st.form("feedback_form"):
        st.subheader("📝 Submit Your Review")
        
        # Star rating selector
        col1, col2 = st.columns([1, 2])
        
        with col1:
            rating = st.select_slider(
                "⭐ Your Rating",
                options=[1, 2, 3, 4, 5],
                value=5,
                help="Select a rating from 1 (poor) to 5 (excellent)"
            )
            
            # Visual star display
            stars = "⭐" * rating + "☆" * (5 - rating)
            st.markdown(f'<div class="star-rating">{stars}</div>', unsafe_allow_html=True)
        
        with col2:
            # Rating description
            rating_descriptions = {
                1: "😞 Poor - Very dissatisfied",
                2: "😕 Fair - Somewhat dissatisfied",
                3: "😐 Good - Neither satisfied nor dissatisfied",
                4: "😊 Very Good - Satisfied",
                5: "🤩 Excellent - Very satisfied"
            }
            st.info(rating_descriptions[rating])
        
        st.markdown("---")
        
        # Review text area
        review_text = st.text_area(
            "✍️ Your Review",
            height=150,
            placeholder="Tell us about your experience... What did you like? What could be improved?",
            help="Please provide detailed feedback to help us serve you better"
        )
        
        # Submit button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submit_button = st.form_submit_button(
                "🚀 Submit Review",
                use_container_width=True,
                type="primary"
            )
    
    # Process submission
    if submit_button:
        if not review_text.strip():
            st.error("❌ Please write a review before submitting!")
        elif len(review_text.strip()) < 10:
            st.error("❌ Please provide a more detailed review (at least 10 characters)")
        else:
            with st.spinner("🤖 Processing your feedback with AI..."):
                try:
                    # Get API key from environment or user input
                    api_key = os.getenv('OPENROUTER_API_KEY')
                    
                    if not api_key:
                        st.error("⚠️ API key not configured. Please set OPENROUTER_API_KEY environment variable.")
                        st.stop()
                    
                    # Initialize LLM handler
                    llm = get_llm_handler(api_key)
                    
                    # Generate AI responses
                    ai_responses = llm.process_feedback(rating, review_text)
                    
                    # Save to database
                    db = get_database()
                    feedback_id = db.insert_feedback(
                        rating=rating,
                        review_text=review_text,
                        user_response=ai_responses['user_response'],
                        admin_summary=ai_responses['admin_summary'],
                        recommended_actions=ai_responses['recommended_actions']
                    )
                    
                    # Store response in session state
                    st.session_state.response_data = {
                        'feedback_id': feedback_id,
                        'rating': rating,
                        'review': review_text,
                        'response': ai_responses['user_response']
                    }
                    st.session_state.submitted = True
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
                    st.info("💡 Make sure your API key is configured correctly.")

else:
    # Show success message and response
    data = st.session_state.response_data
    
    st.success("✅ Thank you! Your review has been submitted successfully!")
    
    # Display submitted rating
    st.markdown("### Your Rating")
    stars = "⭐" * data['rating']
    st.markdown(f'<div class="star-rating">{stars}</div>', unsafe_allow_html=True)
    
    # Display review
    st.markdown("### Your Review")
    st.info(data['review'])
    
    # Display AI response
    st.markdown("### 💬 Our Response")
    st.markdown(f"""
        <div class="response-box">
            <p style="font-size: 1.1rem; margin: 0;">{data['response']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Success footer
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <p style="font-size: 1.1rem; color: #28a745;">
                    ✓ Submission ID: {}</p>
                <p style="color: #666;">Your feedback helps us improve!</p>
            </div>
        """.format(data['feedback_id']), unsafe_allow_html=True)
    
    # Reset button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("📝 Submit Another Review", use_container_width=True):
            st.session_state.submitted = False
            st.session_state.response_data = None
            st.rerun()

# Sidebar information
with st.sidebar:
    st.markdown("### ℹ️ About")
    st.info("""
        This dashboard allows you to:
        - ⭐ Rate your experience (1-5 stars)
        - ✍️ Write detailed feedback
        - 💬 Receive instant AI-generated responses
        
        Your feedback is valuable and helps us improve!
    """)
    
    st.markdown("---")
    
    st.markdown("### 📊 Quick Stats")
    try:
        db = get_database()
        stats = db.get_statistics()
        
        st.metric("Total Reviews", stats['total_submissions'])
        st.metric("Average Rating", f"{stats['average_rating']:.1f} ⭐")
        st.metric("Recent (24h)", stats['recent_submissions_24h'])
    except:
        st.info("No statistics available yet")
    
    st.markdown("---")
    
    # Navigation
    st.markdown("### 🔗 Navigation")
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("app.py")
    if st.button("👨‍💼 Admin Dashboard", use_container_width=True):
        st.switch_page("pages/2_Admin_Dashboard.py")
import streamlit as st
import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_database
from utils.llm_handler import get_llm_handler

# Page configuration
st.set_page_config(
    page_title="User Dashboard - Submit Review",
    page_icon="👤",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .response-box {
        background-color: #f0f2f6;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .star-rating {
        font-size: 2rem;
        color: #ffc107;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'response_data' not in st.session_state:
    st.session_state.response_data = None

# Header
st.markdown('<div class="main-title">👤 User Dashboard</div>', unsafe_allow_html=True)
st.markdown("### Share your experience with us!")

st.markdown("---")

# Main form
if not st.session_state.submitted:
    with st.form("feedback_form"):
        st.subheader("📝 Submit Your Review")
        
        # Star rating selector
        col1, col2 = st.columns([1, 2])
        
        with col1:
            rating = st.select_slider(
                "⭐ Your Rating",
                options=[1, 2, 3, 4, 5],
                value=5,
                help="Select a rating from 1 (poor) to 5 (excellent)"
            )
            
            # Visual star display
            stars = "⭐" * rating + "☆" * (5 - rating)
            st.markdown(f'<div class="star-rating">{stars}</div>', unsafe_allow_html=True)
        
        with col2:
            # Rating description
            rating_descriptions = {
                1: "😞 Poor - Very dissatisfied",
                2: "😕 Fair - Somewhat dissatisfied",
                3: "😐 Good - Neither satisfied nor dissatisfied",
                4: "😊 Very Good - Satisfied",
                5: "🤩 Excellent - Very satisfied"
            }
            st.info(rating_descriptions[rating])
        
        st.markdown("---")
        
        # Review text area
        review_text = st.text_area(
            "✍️ Your Review",
            height=150,
            placeholder="Tell us about your experience... What did you like? What could be improved?",
            help="Please provide detailed feedback to help us serve you better"
        )
        
        # Submit button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submit_button = st.form_submit_button(
                "🚀 Submit Review",
                use_container_width=True,
                type="primary"
            )
    
    # Process submission
    if submit_button:
        if not review_text.strip():
            st.error("❌ Please write a review before submitting!")
        elif len(review_text.strip()) < 10:
            st.error("❌ Please provide a more detailed review (at least 10 characters)")
        else:
            with st.spinner("🤖 Processing your feedback with AI..."):
                try:
                    # Get API key from environment or user input
                    api_key = os.getenv('OPENROUTER_API_KEY')
                    
                    if not api_key:
                        st.error("⚠️ API key not configured. Please set OPENROUTER_API_KEY environment variable.")
                        st.stop()
                    
                    # Initialize LLM handler
                    llm = get_llm_handler(api_key)
                    
                    # Generate AI responses
                    ai_responses = llm.process_feedback(rating, review_text)
                    
                    # Save to database
                    db = get_database()
                    feedback_id = db.insert_feedback(
                        rating=rating,
                        review_text=review_text,
                        user_response=ai_responses['user_response'],
                        admin_summary=ai_responses['admin_summary'],
                        recommended_actions=ai_responses['recommended_actions']
                    )
                    
                    # Store response in session state
                    st.session_state.response_data = {
                        'feedback_id': feedback_id,
                        'rating': rating,
                        'review': review_text,
                        'response': ai_responses['user_response']
                    }
                    st.session_state.submitted = True
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
                    st.info("💡 Make sure your API key is configured correctly.")

else:
    # Show success message and response
    data = st.session_state.response_data
    
    st.success("✅ Thank you! Your review has been submitted successfully!")
    
    # Display submitted rating
    st.markdown("### Your Rating")
    stars = "⭐" * data['rating']
    st.markdown(f'<div class="star-rating">{stars}</div>', unsafe_allow_html=True)
    
    # Display review
    st.markdown("### Your Review")
    st.info(data['review'])
    
    # Display AI response
    st.markdown("### 💬 Our Response")
    st.markdown(f"""
        <div class="response-box">
            <p style="font-size: 1.1rem; margin: 0;">{data['response']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Success footer
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <p style="font-size: 1.1rem; color: #28a745;">
                    ✓ Submission ID: {}</p>
                <p style="color: #666;">Your feedback helps us improve!</p>
            </div>
        """.format(data['feedback_id']), unsafe_allow_html=True)
    
    # Reset button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("📝 Submit Another Review", use_container_width=True):
            st.session_state.submitted = False
            st.session_state.response_data = None
            st.rerun()

# Sidebar information
with st.sidebar:
    st.markdown("### ℹ️ About")
    st.info("""
        This dashboard allows you to:
        - ⭐ Rate your experience (1-5 stars)
        - ✍️ Write detailed feedback
        - 💬 Receive instant AI-generated responses
        
        Your feedback is valuable and helps us improve!
    """)
    
    st.markdown("---")
    
    st.markdown("### 📊 Quick Stats")
    try:
        db = get_database()
        stats = db.get_statistics()
        
        st.metric("Total Reviews", stats['total_submissions'])
        st.metric("Average Rating", f"{stats['average_rating']:.1f} ⭐")
        st.metric("Recent (24h)", stats['recent_submissions_24h'])
    except:
        st.info("No statistics available yet")
    
    st.markdown("---")
    
    # Navigation
    st.markdown("### 🔗 Navigation")
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("app.py")
    if st.button("👨‍💼 Admin Dashboard", use_container_width=True):
        st.switch_page("pages/2_Admin_Dashboard.py")