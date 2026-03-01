"""
Utility functions for data handling and validation.
Supports both CSV (fallback) and Supabase (primary) storage.
"""

import os
import csv
import pandas as pd
from typing import List, Tuple
from datetime import datetime
from supabase_client import (
    init_supabase,
    save_feedback_to_db,
    load_recent_feedback_from_db,
    load_all_feedback_from_db
)

# Configuration
CSV_FILE = "feedback_data.csv"
CSV_COLUMNS = [
    "timestamp",
    "rating",
    "review",
    "ai_response",
    "summary",
    "recommended_actions"
]


def init_csv():
    """Initialize CSV file if it doesn't exist."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
        print(f"✅ Created new CSV file: {CSV_FILE}")
    else:
        print(f"✅ CSV file exists: {CSV_FILE}")


def init_storage():
    """
    Initialize both CSV and Supabase storage.
    Falls back to CSV if Supabase fails.
    """
    print("="*60)
    print("INITIALIZING STORAGE")
    print("="*60)
    
    # Always initialize CSV as fallback
    init_csv()
    
    # Try to initialize Supabase
    supabase_active = init_supabase()
    
    if supabase_active:
        print("\n✅ Primary storage: Supabase")
        print("✅ Fallback storage: CSV")
    else:
        print("\n⚠️  Primary storage: CSV (Supabase unavailable)")
    
    print("="*60)
    return supabase_active


def save_feedback(
    timestamp: str,
    rating: int,
    review: str,
    ai_response: str,
    summary: str,
    actions: List[str]
):
    """
    Save feedback to both Supabase and CSV.
    
    Args:
        timestamp (str): ISO format timestamp
        rating (int): Star rating (1-5)
        review (str): User's review text
        ai_response (str): AI-generated response
        summary (str): AI-generated summary
        actions (List[str]): List of recommended actions
    """
    # Convert actions list to string for CSV
    actions_str = " | ".join(actions)
    
    # Try Supabase first
    db_success = save_feedback_to_db(
        timestamp=timestamp,
        rating=rating,
        review=review,
        ai_response=ai_response,
        summary=summary,
        actions=actions
    )
    
    # Always save to CSV as backup
    try:
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writerow({
                'timestamp': timestamp,
                'rating': rating,
                'review': review,
                'ai_response': ai_response,
                'summary': summary,
                'recommended_actions': actions_str
            })
        print("✅ Feedback saved to CSV")
    except Exception as e:
        print(f"❌ Error saving to CSV: {e}")


def load_recent_feedback(n: int = 5) -> pd.DataFrame:
    """
    Load recent feedback from Supabase or CSV.
    
    Args:
        n (int): Number of recent entries to load
        
    Returns:
        pd.DataFrame: Recent feedback entries
    """
    # Try Supabase first
    db_data = load_recent_feedback_from_db(n)
    
    if db_data:
        # Convert to DataFrame
        df = pd.DataFrame(db_data)
        # Parse actions if needed
        if 'recommended_actions' in df.columns:
            df['recommended_actions'] = df['recommended_actions'].apply(
                lambda x: x if isinstance(x, list) else x.split(' | ')
            )
        return df
    
    # Fallback to CSV
    try:
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            if not df.empty:
                # Parse actions from string to list
                df['recommended_actions'] = df['recommended_actions'].apply(
                    lambda x: x.split(' | ') if isinstance(x, str) else []
                )
                # Return n most recent
                return df.tail(n).iloc[::-1]
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Error loading from CSV: {e}")
        return pd.DataFrame()


def load_all_feedback() -> pd.DataFrame:
    """
    Load all feedback from Supabase or CSV.
    
    Returns:
        pd.DataFrame: All feedback entries
    """
    # Try Supabase first
    db_data = load_all_feedback_from_db()
    
    if db_data:
        df = pd.DataFrame(db_data)
        if 'recommended_actions' in df.columns:
            df['recommended_actions'] = df['recommended_actions'].apply(
                lambda x: x if isinstance(x, list) else x.split(' | ')
            )
        return df
    
    # Fallback to CSV
    try:
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            if not df.empty:
                df['recommended_actions'] = df['recommended_actions'].apply(
                    lambda x: x.split(' | ') if isinstance(x, str) else []
                )
            return df
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Error loading all feedback: {e}")
        return pd.DataFrame()


def validate_input(rating: int, review: str) -> Tuple[bool, str]:
    """
    Validate user input.
    
    Args:
        rating (int): Star rating
        review (str): Review text
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    # Check rating
    if rating < 1 or rating > 5:
        return False, "Please select a rating between 1 and 5 stars."
    
    if rating == 0:
        return False, "Please select a star rating."
    
    # Check review text
    if not review or len(review.strip()) < 10:
        return False, "Please write a review with at least 10 characters."
    
    if len(review) > 2000:
        return False, "Review is too long. Please limit to 2000 characters."
    
    # Check for spam patterns
    if review.lower().count(review.lower().split()[0]) > 10:
        return False, "Review appears to be spam. Please write a genuine review."
    
    return True, ""


def get_rating_emoji(rating: int) -> str:
    """
    Get emoji representation for rating.
    
    Args:
        rating (int): Star rating (1-5)
        
    Returns:
        str: Emoji string
    """
    emoji_map = {
        1: "😞",
        2: "😕",
        3: "😐",
        4: "😊",
        5: "😍"
    }
    return emoji_map.get(rating, "⭐")


def format_timestamp(timestamp_str: str) -> str:
    """
    Format timestamp for display.
    
    Args:
        timestamp_str (str): ISO format timestamp
        
    Returns:
        str: Formatted timestamp
    """
    try:
        dt = datetime.fromisoformat(timestamp_str)
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except:
        return timestamp_str


def calculate_statistics(df: pd.DataFrame) -> dict:
    """
    Calculate statistics from feedback data.
    
    Args:
        df (pd.DataFrame): Feedback dataframe
        
    Returns:
        dict: Statistics dictionary
    """
    if df.empty:
        return {
            'total_count': 0,
            'average_rating': 0,
            'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            'positive_percentage': 0,
            'negative_percentage': 0
        }
    
    total_count = len(df)
    average_rating = df['rating'].mean()
    
    # Rating distribution
    rating_counts = df['rating'].value_counts().to_dict()
    rating_distribution = {i: rating_counts.get(i, 0) for i in range(1, 6)}
    
    # Positive (4-5) and Negative (1-2) percentages
    positive_count = len(df[df['rating'] >= 4])
    negative_count = len(df[df['rating'] <= 2])
    
    positive_percentage = (positive_count / total_count * 100) if total_count > 0 else 0
    negative_percentage = (negative_count / total_count * 100) if total_count > 0 else 0
    
    return {
        'total_count': total_count,
        'average_rating': round(average_rating, 2),
        'rating_distribution': rating_distribution,
        'positive_percentage': round(positive_percentage, 1),
        'negative_percentage': round(negative_percentage, 1)
    }


def export_to_csv(df: pd.DataFrame, filename: str = "feedback_export.csv"):
    """
    Export dataframe to CSV file.
    
    Args:
        df (pd.DataFrame): Dataframe to export
        filename (str): Output filename
    """
    try:
        # Convert lists to strings for CSV
        export_df = df.copy()
        if 'recommended_actions' in export_df.columns:
            export_df['recommended_actions'] = export_df['recommended_actions'].apply(
                lambda x: ' | '.join(x) if isinstance(x, list) else x
            )
        
        export_df.to_csv(filename, index=False)
        print(f"✅ Exported to {filename}")
    except Exception as e:
        print(f"❌ Error exporting: {e}")


# Testing
if __name__ == "__main__":
    print("="*60)
    print("UTILS - TESTING")
    print("="*60)
    
    # Test initialization
    print("\n1. Testing storage initialization...")
    init_storage()
    
    # Test validation
    print("\n2. Testing input validation...")
    test_cases = [
        (0, "Test", "No rating selected"),
        (3, "Short", "Review too short"),
        (5, "This is a valid review with enough characters.", "Valid input"),
    ]
    
    for rating, review, description in test_cases:
        is_valid, error_msg = validate_input(rating, review)
        status = "✅" if is_valid else "❌"
        print(f"{status} {description}: {error_msg if not is_valid else 'Valid'}")
    
    # Test save and load
    print("\n3. Testing save and load...")
    save_feedback(
        timestamp=datetime.now().isoformat(),
        rating=5,
        review="Test review from utils.py",
        ai_response="Thank you for your feedback!",
        summary="Positive test feedback",
        actions=["Action 1", "Action 2"]
    )
    
    recent = load_recent_feedback(5)
    print(f"✅ Loaded {len(recent)} recent entries")
    
    # Test statistics
    print("\n4. Testing statistics...")
    all_data = load_all_feedback()
    stats = calculate_statistics(all_data)
    print(f"Total feedback: {stats['total_count']}")
    print(f"Average rating: {stats['average_rating']}")
    print(f"Positive: {stats['positive_percentage']}%")
    print(f"Negative: {stats['negative_percentage']}%")
    
    print("\n" + "="*60)