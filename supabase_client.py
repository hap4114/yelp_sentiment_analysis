"""
Supabase database client for feedback storage.
Provides persistent, scalable storage with real-time capabilities.
"""

import os
from typing import List, Dict, Optional
from datetime import datetime
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Optional[Client] = None

def init_supabase() -> bool:
    """
    Initialize Supabase client connection.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    global supabase
    
    try:
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("⚠️  Supabase credentials not found. Using CSV fallback.")
            return False
        
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase connection initialized!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize Supabase: {e}")
        return False


def create_feedback_table():
    """
    Creates the feedback table in Supabase if it doesn't exist.
    
    SQL Schema:
    CREATE TABLE feedback (
        id BIGSERIAL PRIMARY KEY,
        timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
        review TEXT NOT NULL,
        ai_response TEXT NOT NULL,
        summary TEXT NOT NULL,
        recommended_actions TEXT[] NOT NULL,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    
    Note: Run this SQL in Supabase Dashboard -> SQL Editor
    """
    print("""
    ⚠️  Please create the table manually in Supabase Dashboard:
    
    1. Go to: https://supabase.com/dashboard/project/YOUR_PROJECT/editor
    2. Click SQL Editor
    3. Run this SQL:
    
    CREATE TABLE feedback (
        id BIGSERIAL PRIMARY KEY,
        timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
        review TEXT NOT NULL,
        ai_response TEXT NOT NULL,
        summary TEXT NOT NULL,
        recommended_actions TEXT[] NOT NULL,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    
    4. Enable Row Level Security (RLS) if needed
    """)


def save_feedback_to_db(
    timestamp: str,
    rating: int,
    review: str,
    ai_response: str,
    summary: str,
    actions: List[str]
) -> bool:
    """
    Saves feedback to Supabase database.
    
    Args:
        timestamp (str): ISO format timestamp
        rating (int): Rating (1-5)
        review (str): User's review text
        ai_response (str): AI-generated response
        summary (str): AI-generated summary
        actions (List[str]): List of recommended actions
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not supabase:
        print("⚠️  Supabase not initialized. Data not saved to database.")
        return False
    
    try:
        # Prepare data
        data = {
            "timestamp": timestamp,
            "rating": rating,
            "review": review,
            "ai_response": ai_response,
            "summary": summary,
            "recommended_actions": actions  # Supabase handles arrays natively
        }
        
        # Insert into database
        result = supabase.table("feedback").insert(data).execute()
        
        if result.data:
            print(f"✅ Feedback saved to Supabase (ID: {result.data[0]['id']})")
            return True
        else:
            print("❌ Failed to save to Supabase")
            return False
            
    except Exception as e:
        print(f"❌ Error saving to Supabase: {e}")
        return False


def load_recent_feedback_from_db(n: int = 5) -> List[Dict]:
    """
    Loads the most recent n feedback entries from database.
    
    Args:
        n (int): Number of entries to load (default: 5)
        
    Returns:
        List[Dict]: List of feedback entries
    """
    if not supabase:
        print("⚠️  Supabase not initialized.")
        return []
    
    try:
        # Query recent feedback, sorted by timestamp descending
        result = supabase.table("feedback") \
            .select("*") \
            .order("timestamp", desc=True) \
            .limit(n) \
            .execute()
        
        return result.data if result.data else []
        
    except Exception as e:
        print(f"❌ Error loading from Supabase: {e}")
        return []


def load_all_feedback_from_db() -> List[Dict]:
    """
    Loads all feedback entries from database.
    
    Returns:
        List[Dict]: List of all feedback entries
    """
    if not supabase:
        print("⚠️  Supabase not initialized.")
        return []
    
    try:
        result = supabase.table("feedback") \
            .select("*") \
            .order("timestamp", desc=True) \
            .execute()
        
        return result.data if result.data else []
        
    except Exception as e:
        print(f"❌ Error loading all feedback from Supabase: {e}")
        return []


def get_feedback_stats_from_db() -> Dict:
    """
    Calculates statistics from database.
    
    Returns:
        Dict: Statistics including counts, averages, distributions
    """
    if not supabase:
        return {
            "total_count": 0,
            "average_rating": 0,
            "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            "positive_percentage": 0,
            "negative_percentage": 0
        }
    
    try:
        # Get all feedback
        all_feedback = load_all_feedback_from_db()
        
        if not all_feedback:
            return {
                "total_count": 0,
                "average_rating": 0,
                "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                "positive_percentage": 0,
                "negative_percentage": 0
            }
        
        # Calculate statistics
        total_count = len(all_feedback)
        ratings = [f['rating'] for f in all_feedback]
        average_rating = sum(ratings) / total_count
        
        # Rating distribution
        rating_distribution = {i: ratings.count(i) for i in range(1, 6)}
        
        # Positive (4-5) and Negative (1-2) percentages
        positive_count = sum(1 for r in ratings if r >= 4)
        negative_count = sum(1 for r in ratings if r <= 2)
        
        positive_percentage = (positive_count / total_count * 100) if total_count > 0 else 0
        negative_percentage = (negative_count / total_count * 100) if total_count > 0 else 0
        
        return {
            "total_count": total_count,
            "average_rating": round(average_rating, 2),
            "rating_distribution": rating_distribution,
            "positive_percentage": round(positive_percentage, 1),
            "negative_percentage": round(negative_percentage, 1)
        }
        
    except Exception as e:
        print(f"❌ Error calculating stats: {e}")
        return {
            "total_count": 0,
            "average_rating": 0,
            "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            "positive_percentage": 0,
            "negative_percentage": 0
        }


def get_feedback_by_rating(rating: int) -> List[Dict]:
    """
    Gets all feedback with a specific rating.
    
    Args:
        rating (int): Rating to filter by (1-5)
        
    Returns:
        List[Dict]: Filtered feedback entries
    """
    if not supabase:
        return []
    
    try:
        result = supabase.table("feedback") \
            .select("*") \
            .eq("rating", rating) \
            .order("timestamp", desc=True) \
            .execute()
        
        return result.data if result.data else []
        
    except Exception as e:
        print(f"❌ Error filtering by rating: {e}")
        return []


def get_feedback_by_date_range(start_date: str, end_date: str) -> List[Dict]:
    """
    Gets feedback within a date range.
    
    Args:
        start_date (str): Start date (ISO format)
        end_date (str): End date (ISO format)
        
    Returns:
        List[Dict]: Feedback within date range
    """
    if not supabase:
        return []
    
    try:
        result = supabase.table("feedback") \
            .select("*") \
            .gte("timestamp", start_date) \
            .lte("timestamp", end_date) \
            .order("timestamp", desc=True) \
            .execute()
        
        return result.data if result.data else []
        
    except Exception as e:
        print(f"❌ Error filtering by date: {e}")
        return []


def search_feedback(keyword: str) -> List[Dict]:
    """
    Searches feedback by keyword in review text.
    
    Args:
        keyword (str): Keyword to search for
        
    Returns:
        List[Dict]: Matching feedback entries
    """
    if not supabase:
        return []
    
    try:
        result = supabase.table("feedback") \
            .select("*") \
            .ilike("review", f"%{keyword}%") \
            .order("timestamp", desc=True) \
            .execute()
        
        return result.data if result.data else []
        
    except Exception as e:
        print(f"❌ Error searching feedback: {e}")
        return []


def delete_feedback(feedback_id: int) -> bool:
    """
    Deletes a feedback entry by ID.
    
    Args:
        feedback_id (int): ID of feedback to delete
        
    Returns:
        bool: True if successful
    """
    if not supabase:
        return False
    
    try:
        result = supabase.table("feedback") \
            .delete() \
            .eq("id", feedback_id) \
            .execute()
        
        if result.data:
            print(f"✅ Deleted feedback ID: {feedback_id}")
            return True
        return False
        
    except Exception as e:
        print(f"❌ Error deleting feedback: {e}")
        return False


def test_supabase_connection():
    """
    Tests Supabase connection and table access.
    
    Returns:
        bool: True if connection and table access successful
    """
    if not init_supabase():
        return False
    
    try:
        # Try to query the table
        result = supabase.table("feedback").select("*").limit(1).execute()
        print("✅ Supabase table access successful!")
        return True
        
    except Exception as e:
        print(f"❌ Supabase table access failed: {e}")
        print("\n📝 Make sure you've created the 'feedback' table!")
        print("Run create_feedback_table() for SQL schema.")
        return False


# Testing
if __name__ == "__main__":
    print("="*60)
    print("SUPABASE CLIENT - TESTING")
    print("="*60)
    
    # Test connection
    print("\n1. Testing Supabase connection...")
    if test_supabase_connection():
        print("✅ Connection successful!")
        
        # Test save
        print("\n2. Testing save operation...")
        success = save_feedback_to_db(
            timestamp=datetime.now().isoformat(),
            rating=5,
            review="Test review from supabase_client.py",
            ai_response="Test AI response",
            summary="Test summary",
            actions=["Test action 1", "Test action 2"]
        )
        
        if success:
            print("✅ Save successful!")
            
            # Test load
            print("\n3. Testing load operation...")
            recent = load_recent_feedback_from_db(5)
            print(f"✅ Loaded {len(recent)} recent entries")
            
            # Test stats
            print("\n4. Testing statistics...")
            stats = get_feedback_stats_from_db()
            print(f"✅ Total feedback: {stats['total_count']}")
            print(f"✅ Average rating: {stats['average_rating']}")
    else:
        print("❌ Connection failed. Check your credentials.")
        print("\n📝 Setup Instructions:")
        print("1. Get credentials from Supabase Dashboard")
        print("2. Add to .env file:")
        print("   SUPABASE_URL=your_project_url")
        print("   SUPABASE_KEY=your_anon_key")
        print("3. Create the feedback table (see create_feedback_table())")
    
    print("\n" + "="*60)