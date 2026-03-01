import streamlit as st
import pandas as pd
import os
from datetime import datetime
from llm_client import get_feedback_analysis
from utils import init_storage, save_feedback, load_recent_feedback, validate_input

# Page configuration
st.set_page_config(
    page_title="Restaurant Feedback System",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS with your color scheme
st.markdown("""
<style>
    /* Color Variables */
    :root {
        --sage-green: #6B8E23;
        --charcoal: #36454F;
        --gold: #FFC72C;
        --cream: #FAF9F6;
        --tan: #E7E5DF;
    }
    
    /* Main container */
    .main {
        background-color: #FAF9F6;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #6B8E23 0%, #556B2F 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .header-title {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-align: center;
    }
    
    .header-subtitle {
        color: #FAF9F6;
        font-size: 1.1rem;
        text-align: center;
        margin-top: 0.5rem;
    }
    
    /* Star rating */
    .star-container {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin: 1.5rem 0;
    }
    
    .star {
        font-size: 3rem;
        cursor: pointer;
        transition: all 0.2s;
        color: #E7E5DF;
    }
    
    .star.selected {
        color: #FFC72C;
        transform: scale(1.1);
    }
    
    .star:hover {
        transform: scale(1.2);
    }
    
    /* Card styling */
    .feedback-card {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #E7E5DF;
        margin-bottom: 1.5rem;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #6B8E23 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        width: 100%;
        transition: all 0.3s !important;
    }
    
    .stButton > button:hover {
        background-color: #556B2F !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(107,142,35,0.3) !important;
    }
    
    /* AI Response styling */
    .ai-response {
        background: linear-gradient(135deg, #f8f9fa 0%, #FAF9F6 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #6B8E23;
        margin: 1.5rem 0;
    }
    
    .ai-response-title {
        color: #6B8E23;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    /* Success message */
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Recent feedback */
    .recent-item {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid #FFC72C;
        margin-bottom: 0.8rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
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
    
    /* Textarea styling */
    .stTextArea textarea {
        border: 2px solid #E7E5DF !important;
        border-radius: 8px !important;
        font-size: 1rem !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #6B8E23 !important;
        box-shadow: 0 0 0 2px rgba(107,142,35,0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize storage (CSV + Supabase)
init_storage()

# Header
st.markdown("""
<div class="header-container">
    <h1 class="header-title">🍽️ Restaurant Feedback System</h1>
    <p class="header-subtitle">Share your experience and get instant AI-powered responses</p>
</div>
""", unsafe_allow_html=True)

# Main feedback form
st.markdown('<div class="feedback-card">', unsafe_allow_html=True)

# Star Rating Section
st.markdown("### ⭐ Rate Your Experience")

# Create star rating using columns
col1, col2, col3, col4, col5 = st.columns(5)
rating_labels = {
    1: "1 - Very Poor",
    2: "2 - Poor", 
    3: "3 - Average",
    4: "4 - Good",
    5: "5 - Excellent"
}

# Initialize session state for rating
if 'selected_rating' not in st.session_state:
    st.session_state.selected_rating = 0

# Star buttons
stars = []
with col1:
    if st.button("⭐", key="star1", help="1 Star", use_container_width=True):
        st.session_state.selected_rating = 1
with col2:
    if st.button("⭐", key="star2", help="2 Stars", use_container_width=True):
        st.session_state.selected_rating = 2
with col3:
    if st.button("⭐", key="star3", help="3 Stars", use_container_width=True):
        st.session_state.selected_rating = 3
with col4:
    if st.button("⭐", key="star4", help="4 Stars", use_container_width=True):
        st.session_state.selected_rating = 4
with col5:
    if st.button("⭐", key="star5", help="5 Stars", use_container_width=True):
        st.session_state.selected_rating = 5

# Display selected rating
if st.session_state.selected_rating > 0:
    stars_display = "⭐" * st.session_state.selected_rating + "☆" * (5 - st.session_state.selected_rating)
    st.markdown(f"<p style='text-align: center; font-size: 1.2rem; color: #FFC72C;'>{stars_display} {rating_labels[st.session_state.selected_rating]}</p>", unsafe_allow_html=True)
else:
    st.info("👆 Click on the stars above to select your rating")

st.markdown("---")

# Review Text Area
st.markdown("### 📝 Share Your Feedback")
review_text = st.text_area(
    "",
    placeholder="Tell us about your experience... (e.g., food quality, service, ambience, wait time)",
    height=150,
    help="Please share your honest feedback. Avoid personal information.",
    label_visibility="collapsed"
)

st.markdown("---")

# Submit Button
submit_button = st.button("🚀 Submit Feedback", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Handle submission
if submit_button:
    rating = st.session_state.selected_rating
    
    # Validate input
    is_valid, error_msg = validate_input(rating, review_text)
    
    if not is_valid:
        st.error(f"❌ {error_msg}")
    else:
        # Show loading spinner
        with st.spinner("🤖 Generating AI response... Please wait."):
            try:
                # Call LLM
                analysis = get_feedback_analysis(rating, review_text)
                
                if analysis:
                    # Save to CSV
                    timestamp = datetime.now().isoformat()
                    save_feedback(
                        timestamp=timestamp,
                        rating=rating,
                        review=review_text,
                        ai_response=analysis['user_response'],
                        summary=analysis['summary'],
                        actions=analysis['recommended_actions']
                    )
                    
                    # Success message
                    st.markdown('<div class="success-message">✅ Thank you! Your feedback has been submitted successfully.</div>', unsafe_allow_html=True)
                    
                    # Display AI Response
                    st.markdown('<div class="ai-response">', unsafe_allow_html=True)
                    st.markdown('<div class="ai-response-title">🤖 Our Response to You</div>', unsafe_allow_html=True)
                    st.markdown(f"<p style='color: #36454F; font-size: 1.05rem; line-height: 1.6;'>{analysis['user_response']}</p>", unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Show summary and actions in expander
                    with st.expander("📊 See what we learned from your feedback"):
                        st.markdown(f"**Summary:** {analysis['summary']}")
                        st.markdown("**Actions we'll take:**")
                        for i, action in enumerate(analysis['recommended_actions'], 1):
                            st.markdown(f"{i}. {action}")
                    
                    # Reset rating
                    st.session_state.selected_rating = 0
                    st.rerun()
                    
                else:
                    st.error("❌ Failed to generate AI response. Please try again.")
                    
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.info("Please check your API key and try again.")

# Recent Feedback Section
st.markdown("---")
st.markdown("### 📜 Recent Feedback (Positive to Negative)")

recent_feedback = load_recent_feedback(n=5)

if not recent_feedback.empty:
    # Sort by rating (5 to 1)
    recent_feedback = recent_feedback.sort_values('rating', ascending=False)
    
    for _, row in recent_feedback.iterrows():
        rating_class = f"rating-{row['rating']}"
        stars = "⭐" * row['rating']
        
        # Truncate review if too long
        review_preview = row['review'][:100] + "..." if len(row['review']) > 100 else row['review']
        
        # Calculate time ago
        try:
            timestamp = pd.to_datetime(row['timestamp'])
            time_ago = (datetime.now() - timestamp).total_seconds() / 60
            if time_ago < 1:
                time_str = "Just now"
            elif time_ago < 60:
                time_str = f"{int(time_ago)} min ago"
            else:
                time_str = f"{int(time_ago/60)} hours ago"
        except:
            time_str = "Recently"
        
        st.markdown(f"""
        <div class="recent-item">
            <span class="rating-badge {rating_class}">{stars} {row['rating']}/5</span>
            <span style="color: #888; font-size: 0.9rem;">{time_str}</span>
            <p style="margin: 0.5rem 0 0 0; color: #36454F;">{review_preview}</p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No feedback submissions yet. Be the first to share your experience!")

# Footer
st.markdown("---")
st.markdown("""
<p style='text-align: center; color: #888; font-size: 0.9rem;'>
    © 2025 AI Feedback System · Powered by Gemini AI · User Dashboard
</p>
""", unsafe_allow_html=True)