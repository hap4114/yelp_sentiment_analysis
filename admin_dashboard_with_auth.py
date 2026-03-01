"""
Admin Dashboard for Restaurant Feedback System
Password-protected interface with analytics and feedback management.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import hashlib
import os
from utils import (
    init_storage,
    load_all_feedback,
    calculate_statistics,
    format_timestamp,
    export_to_csv
)

# Page configuration
st.set_page_config(
    page_title="Admin Dashboard - Restaurant Feedback",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #FAF9F6;
    }
    
    /* Login container */
    .login-container {
        max-width: 400px;
        margin: 100px auto;
        padding: 2rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-top: 4px solid #6B8E23;
    }
    
    .login-title {
        text-align: center;
        color: #6B8E23;
        font-size: 2rem;
        margin-bottom: 1rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #6B8E23;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #6B8E23;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .feedback-item {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 4px solid #FFC72C;
    }
    
    .rating-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    
    .rating-5 { background-color: #d4edda; color: #155724; }
    .rating-4 { background-color: #d1ecf1; color: #0c5460; }
    .rating-3 { background-color: #fff3cd; color: #856404; }
    .rating-2 { background-color: #f8d7da; color: #721c24; }
    .rating-1 { background-color: #f8d7da; color: #721c24; }
    
    .action-item {
        background: #f8f9fa;
        padding: 0.8rem;
        margin: 0.3rem 0;
        border-radius: 5px;
        border-left: 3px solid #6B8E23;
    }
    
    h1, h2, h3 {
        color: #36454F;
    }
    
    .stButton > button {
        background-color: #6B8E23 !important;
        color: white !important;
    }
    
    .logout-btn {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
    }
</style>
""", unsafe_allow_html=True)

# Admin credentials (in production, use environment variables or database)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")  # Change this!

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(username, password):
    """Verify username and password"""
    return username == ADMIN_USERNAME and hash_password(password) == hash_password(ADMIN_PASSWORD)

def login_page():
    """Display login page"""
    st.markdown("""
    <div class="login-container">
        <div class="login-title">🔐 Admin Login</div>
        <p style='text-align: center; color: #666; margin-bottom: 2rem;'>
            Enter your credentials to access the admin dashboard
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create centered columns
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Enter username")
            password = st.text_input("🔑 Password", type="password", placeholder="Enter password")
            submit = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if submit:
                if check_password(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success("✅ Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
        
        st.markdown("---")
        st.info("""
        **Default Credentials:**
        - Username: `admin`
        - Password: `admin123`
        
        ⚠️ Change these in production!
        """)
        
        # Back to user dashboard link
        st.markdown("""
        <div style='text-align: center; margin-top: 2rem;'>
            <a href='http://localhost:8501' target='_blank' style='color: #6B8E23; text-decoration: none;'>
                ← Back to User Dashboard
            </a>
        </div>
        """, unsafe_allow_html=True)

def logout():
    """Logout and clear session"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()

def admin_dashboard():
    """Display admin dashboard"""
    
    # Logout button in sidebar
    with st.sidebar:
        st.markdown(f"### 👤 Logged in as: **{st.session_state.username}**")
        if st.button("🚪 Logout", use_container_width=True):
            logout()
        st.markdown("---")
    
    # Initialize storage
    init_storage()
    
    # Header
    st.title("📊 Admin Dashboard")
    st.markdown("### Restaurant Feedback Analytics & Management")
    st.markdown("---")
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Rating filter
    rating_filter = st.sidebar.multiselect(
        "Filter by Rating",
        options=[1, 2, 3, 4, 5],
        default=[1, 2, 3, 4, 5]
    )
    
    # Search
    search_term = st.sidebar.text_input("🔎 Search Reviews", "")
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.rerun()
    
    # Load data
    all_feedback = load_all_feedback()
    
    # Apply filters
    if not all_feedback.empty:
        # Filter by rating
        filtered_data = all_feedback[all_feedback['rating'].isin(rating_filter)]
        
        # Filter by search term
        if search_term:
            filtered_data = filtered_data[
                filtered_data['review'].str.contains(search_term, case=False, na=False)
            ]
    else:
        filtered_data = pd.DataFrame()
    
    # Calculate statistics
    stats = calculate_statistics(all_feedback)
    
    # Display metrics
    st.markdown("## 📈 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Feedback",
            value=stats['total_count'],
            delta=None
        )
    
    with col2:
        st.metric(
            label="Average Rating",
            value=f"{stats['average_rating']:.1f} ⭐",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Positive Rate",
            value=f"{stats['positive_percentage']}%",
            delta=None
        )
    
    with col4:
        st.metric(
            label="Negative Rate",
            value=f"{stats['negative_percentage']}%",
            delta=None
        )
    
    st.markdown("---")
    
    # Charts
    if not all_feedback.empty:
        st.markdown("## 📊 Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Rating distribution
            rating_dist = pd.DataFrame(
                list(stats['rating_distribution'].items()),
                columns=['Rating', 'Count']
            )
            
            fig = px.bar(
                rating_dist,
                x='Rating',
                y='Count',
                title="Rating Distribution",
                color='Count',
                color_continuous_scale='Greens'
            )
            fig.update_layout(
                showlegend=False,
                xaxis_title="Star Rating",
                yaxis_title="Number of Reviews"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Sentiment pie chart
            sentiment_data = pd.DataFrame({
                'Sentiment': ['Positive (4-5★)', 'Neutral (3★)', 'Negative (1-2★)'],
                'Count': [
                    len(all_feedback[all_feedback['rating'] >= 4]),
                    len(all_feedback[all_feedback['rating'] == 3]),
                    len(all_feedback[all_feedback['rating'] <= 2])
                ]
            })
            
            fig = px.pie(
                sentiment_data,
                values='Count',
                names='Sentiment',
                title="Sentiment Distribution",
                color='Sentiment',
                color_discrete_map={
                    'Positive (4-5★)': '#d4edda',
                    'Neutral (3★)': '#fff3cd',
                    'Negative (1-2★)': '#f8d7da'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
    
    # Feedback list
    st.markdown(f"## 📝 Feedback List ({len(filtered_data)} items)")
    
    if not filtered_data.empty:
        # Sort by timestamp (most recent first)
        filtered_data = filtered_data.sort_values('timestamp', ascending=False)
        
        # Display each feedback item
        for idx, row in filtered_data.iterrows():
            rating_class = f"rating-{row['rating']}"
            stars = "⭐" * row['rating']
            
            # Create expander for each feedback
            with st.expander(
                f"{stars} {row['rating']}/5 - {row['review'][:80]}..." if len(row['review']) > 80 else f"{stars} {row['rating']}/5 - {row['review']}",
                expanded=False
            ):
                # Timestamp
                st.markdown(f"**🕐 Submitted:** {format_timestamp(row['timestamp'])}")
                
                # Rating
                st.markdown(f"**⭐ Rating:** {row['rating']}/5 stars")
                
                # Review
                st.markdown("**💬 Customer Review:**")
                st.info(row['review'])
                
                # AI Response
                st.markdown("**🤖 AI Response to Customer:**")
                st.success(row['ai_response'])
                
                # Summary
                st.markdown("**📋 Internal Summary:**")
                st.warning(row['summary'])
                
                # Actions
                st.markdown("**✅ Recommended Actions:**")
                actions = row['recommended_actions']
                if isinstance(actions, str):
                    actions = actions.split(' | ')
                for i, action in enumerate(actions, 1):
                    st.markdown(f"{i}. {action}")
                
                st.markdown("---")
        
        # Export button
        if st.button("📥 Export All Data to CSV"):
            export_to_csv(all_feedback, "admin_feedback_export.csv")
            st.success("✅ Data exported to admin_feedback_export.csv")
    
    else:
        if search_term:
            st.info(f"No feedback found matching '{search_term}'")
        else:
            st.info("No feedback submissions yet.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <p style='text-align: center; color: #888; font-size: 0.9rem;'>
        © 2025 AI Feedback System · Powered by Gemini AI · Admin Dashboard
    </p>
    """, unsafe_allow_html=True)

# Main application logic
def main():
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    
    # Show login or dashboard based on authentication
    if st.session_state.authenticated:
        admin_dashboard()
    else:
        login_page()

if __name__ == "__main__":
    main()