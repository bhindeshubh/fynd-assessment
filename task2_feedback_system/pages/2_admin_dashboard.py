import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_database

# Page configuration
st.set_page_config(
    page_title="Admin Dashboard - Feedback Analytics",
    page_icon="👨‍💼",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .feedback-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ddd;
        margin: 0.5rem 0;
    }
    .positive-feedback {
        border-left: 4px solid #28a745;
    }
    .negative-feedback {
        border-left: 4px solid #dc3545;
    }
    .neutral-feedback {
        border-left: 4px solid #ffc107;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize database
db = get_database()

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<div class="main-title">👨‍💼 Admin Dashboard</div>', unsafe_allow_html=True)
    st.markdown("### Real-time Feedback Analytics & Management")

with col2:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

st.markdown("---")

# Get data
try:
    df = db.get_all_feedback()
    stats = db.get_statistics()
    
    if len(df) == 0:
        st.info("📭 No feedback submissions yet. Check back after users submit reviews!")
        st.stop()
    
except Exception as e:
    st.error(f"❌ Error loading data: {str(e)}")
    st.stop()

# ============================================================================
# KEY METRICS
# ============================================================================

st.markdown("## 📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Submissions",
        value=stats['total_submissions'],
        delta=f"+{stats['recent_submissions_24h']} (24h)"
    )

with col2:
    avg_rating = stats['average_rating']
    st.metric(
        label="Average Rating",
        value=f"{avg_rating:.2f} ⭐",
        delta=f"{avg_rating - 3:.2f} vs neutral" if avg_rating != 0 else None
    )

with col3:
    positive_count = len(df[df['rating'] >= 4])
    positive_pct = (positive_count / len(df) * 100) if len(df) > 0 else 0
    st.metric(
        label="Positive Reviews",
        value=f"{positive_pct:.1f}%",
        delta=f"{positive_count} reviews"
    )

with col4:
    negative_count = len(df[df['rating'] <= 2])
    negative_pct = (negative_count / len(df) * 100) if len(df) > 0 else 0
    st.metric(
        label="Needs Attention",
        value=f"{negative_count}",
        delta=f"{negative_pct:.1f}% of total",
        delta_color="inverse"
    )

st.markdown("---")

# ============================================================================
# VISUALIZATIONS
# ============================================================================

st.markdown("## 📈 Analytics")

col1, col2 = st.columns(2)

with col1:
    # Rating distribution
    st.markdown("### ⭐ Rating Distribution")
    
    rating_counts = df['rating'].value_counts().sort_index()
    
    fig = go.Figure(data=[
        go.Bar(
            x=[f"{i} ⭐" for i in rating_counts.index],
            y=rating_counts.values,
            marker_color=['#dc3545', '#fd7e14', '#ffc107', '#28a745', '#20c997'],
            text=rating_counts.values,
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        xaxis_title="Rating",
        yaxis_title="Number of Reviews",
        height=300,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Rating trend over time
    st.markdown("### 📅 Ratings Over Time")
    
    df_sorted = df.sort_values('timestamp')
    
    fig = px.scatter(
        df_sorted,
        x='timestamp',
        y='rating',
        color='rating',
        color_continuous_scale=['red', 'orange', 'yellow', 'lightgreen', 'green'],
        size_max=10,
        height=300
    )
    
    fig.update_layout(
        xaxis_title="Submission Time",
        yaxis_title="Rating",
        yaxis=dict(tickvals=[1, 2, 3, 4, 5]),
        coloraxis_showscale=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================================
# FILTERS
# ============================================================================

st.markdown("## 🔍 Feedback Explorer")

col1, col2, col3 = st.columns(3)

with col1:
    filter_rating = st.multiselect(
        "Filter by Rating",
        options=[1, 2, 3, 4, 5],
        default=[1, 2, 3, 4, 5],
        format_func=lambda x: f"{x} ⭐"
    )

with col2:
    sort_order = st.selectbox(
        "Sort by",
        options=["Newest First", "Oldest First", "Highest Rating", "Lowest Rating"],
        index=0
    )

with col3:
    show_count = st.slider(
        "Number of reviews to display",
        min_value=1,
        max_value=min(50, len(df)),
        value=min(10, len(df))
    )

# Apply filters
filtered_df = df[df['rating'].isin(filter_rating)].copy()

# Apply sorting
if sort_order == "Newest First":
    filtered_df = filtered_df.sort_values('timestamp', ascending=False)
elif sort_order == "Oldest First":
    filtered_df = filtered_df.sort_values('timestamp', ascending=True)
elif sort_order == "Highest Rating":
    filtered_df = filtered_df.sort_values(['rating', 'timestamp'], ascending=[False, False])
else:  # Lowest Rating
    filtered_df = filtered_df.sort_values(['rating', 'timestamp'], ascending=[True, False])

# Limit display
display_df = filtered_df.head(show_count)

st.markdown(f"### Showing {len(display_df)} of {len(filtered_df)} filtered reviews")

# ============================================================================
# FEEDBACK CARDS
# ============================================================================

for idx, row in display_df.iterrows():
    # Determine card class based on rating
    if row['rating'] >= 4:
        card_class = "positive-feedback"
        sentiment_emoji = "😊"
    elif row['rating'] <= 2:
        card_class = "negative-feedback"
        sentiment_emoji = "😞"
    else:
        card_class = "neutral-feedback"
        sentiment_emoji = "😐"
    
    # Create expandable card
    with st.expander(
        f"{sentiment_emoji} {'⭐' * row['rating']} | {row['timestamp']} | ID: {row['id']}",
        expanded=False
    ):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 📝 Customer Review")
            st.write(row['review_text'])
            
            st.markdown("#### 💬 User Response Sent")
            st.info(row['user_response'])
        
        with col2:
            st.markdown("#### 📊 AI Summary")
            st.success(row['admin_summary'])
            
            st.markdown("#### ✅ Recommended Actions")
            st.warning(row['recommended_actions'])
            
            # Metadata
            st.markdown("---")
            st.caption(f"**Submission ID:** {row['id']}")
            st.caption(f"**Timestamp:** {row['timestamp']}")
            st.caption(f"**Rating:** {row['rating']} stars")

st.markdown("---")

# ============================================================================
# EXPORT & MANAGEMENT
# ============================================================================

st.markdown("## 🛠️ Data Management")

col1, col2, col3 = st.columns(3)

with col1:
    # Export to CSV
    if st.button("📥 Export All Data to CSV", use_container_width=True):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"exports/feedback_export_{timestamp}.csv"
            
            os.makedirs("exports", exist_ok=True)
            count = db.export_to_csv(filename)
            
            st.success(f"✅ Exported {count} records to {filename}")
            
            # Provide download button
            with open(filename, 'rb') as f:
                st.download_button(
                    label="💾 Download CSV",
                    data=f,
                    file_name=f"feedback_export_{timestamp}.csv",
                    mime="text/csv"
                )
        except Exception as e:
            st.error(f"❌ Export failed: {str(e)}")

with col2:
    # Show statistics
    if st.button("📊 View Detailed Statistics", use_container_width=True):
        st.json(stats)

with col3:
    # Clear data (with confirmation)
    if st.button("🗑️ Clear All Data", use_container_width=True, type="secondary"):
        st.warning("⚠️ This action cannot be undone!")
        if st.button("⚠️ Confirm Delete All", type="primary"):
            db.clear_all_data()
            st.success("✅ All data cleared!")
            st.rerun()

# Sidebar
with st.sidebar:
    st.markdown("### ℹ️ Dashboard Info")
    st.info("""
        This admin dashboard provides:
        - 📊 Real-time analytics
        - 📋 All customer submissions
        - 🤖 AI-generated insights
        - ✅ Action recommendations
        - 📥 Data export capabilities
    """)
    
    st.markdown("---")
    
    st.markdown("### 📈 Quick Insights")
    
    if len(df) > 0:
        # Most common rating
        most_common = df['rating'].mode()[0]
        st.metric("Most Common Rating", f"{most_common} ⭐")
        
        # Average review length
        avg_length = df['review_text'].str.len().mean()
        st.metric("Avg Review Length", f"{int(avg_length)} chars")
        
        # Percentage of each rating
        st.markdown("#### Rating Breakdown")
        for rating in [5, 4, 3, 2, 1]:
            count = len(df[df['rating'] == rating])
            pct = (count / len(df) * 100) if len(df) > 0 else 0
            st.write(f"{'⭐' * rating}: {pct:.1f}% ({count})")
    
    st.markdown("---")
    
    # Navigation
    st.markdown("### 🔗 Navigation")
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("app.py")
    if st.button("👤 User Dashboard", use_container_width=True):
        st.switch_page("pages/1_User_Dashboard.py")
    
    st.markdown("---")
    
    st.markdown("### ⚙️ Settings")
    auto_refresh = st.checkbox("Auto-refresh (30s)", value=False)
    
    if auto_refresh:
        import time
        time.sleep(30)
        st.rerun()