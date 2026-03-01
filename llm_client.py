"""
LLM Client for feedback analysis using Google Gemini API.
Handles all AI interactions for generating responses, summaries, and action items.
"""

import os
import google.generativeai as genai
from typing import Dict, Optional
from prompts import (
    get_user_response_prompt,
    get_summary_prompt,
    get_actions_prompt
)

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")

def init_gemini():
    """Initialize Gemini API with API key."""
    if not API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    genai.configure(api_key=API_KEY)
    print("✅ Gemini API initialized!")


def generate_text(prompt: str, temperature: float = 0.7) -> Optional[str]:
    """
    Generate text using Gemini API.
    
    Args:
        prompt (str): The prompt to send to the model
        temperature (float): Sampling temperature (0.0-1.0)
        
    Returns:
        Optional[str]: Generated text or None if failed
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=1024,
            )
        )
        return response.text
    except Exception as e:
        print(f"❌ Error generating text: {e}")
        return None


def get_feedback_analysis(rating: int, review: str) -> Optional[Dict]:
    """
    Generate complete feedback analysis including:
    - User-facing response
    - Internal summary
    - Recommended actions
    
    Args:
        rating (int): Star rating (1-5)
        review (str): User's review text
        
    Returns:
        Optional[Dict]: Analysis dictionary or None if failed
    """
    try:
        # Initialize Gemini
        init_gemini()
        
        # Generate user response
        user_response_prompt = get_user_response_prompt(rating, review)
        user_response = generate_text(user_response_prompt, temperature=0.8)
        
        if not user_response:
            return None
        
        # Generate internal summary
        summary_prompt = get_summary_prompt(rating, review)
        summary = generate_text(summary_prompt, temperature=0.5)
        
        if not summary:
            return None
        
        # Generate recommended actions
        actions_prompt = get_actions_prompt(rating, review, summary)
        actions_text = generate_text(actions_prompt, temperature=0.6)
        
        if not actions_text:
            return None
        
        # Parse actions (split by newlines and clean)
        actions = [
            action.strip().lstrip('0123456789.-) ')
            for action in actions_text.split('\n')
            if action.strip() and len(action.strip()) > 5
        ][:5]  # Limit to 5 actions
        
        return {
            'user_response': user_response.strip(),
            'summary': summary.strip(),
            'recommended_actions': actions
        }
        
    except Exception as e:
        print(f"❌ Error in feedback analysis: {e}")
        return None


def test_gemini_connection() -> bool:
    """
    Test Gemini API connection.
    
    Returns:
        bool: True if connection successful
    """
    try:
        init_gemini()
        
        # Test with a simple prompt
        test_prompt = "Say 'Hello' if you can hear me."
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(test_prompt)
        
        if response.text:
            print("✅ Gemini API connection successful!")
            print(f"📝 Test response: {response.text[:50]}...")
            return True
        else:
            print("❌ Gemini API returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API connection failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your API key is correct")
        print("2. Verify your API key is active at: https://makersuite.google.com/app/apikey")
        print("3. Ensure you have API quota remaining")
        return False


# Testing
if __name__ == "__main__":
    print("="*60)
    print("LLM CLIENT - TESTING")
    print("="*60)
    
    # Test connection
    print("\n1. Testing Gemini connection...")
    if test_gemini_connection():
        
        # Test feedback analysis
        print("\n2. Testing feedback analysis...")
        print("-"*60)
        
        test_rating = 5
        test_review = "Amazing food and excellent service! The pasta was delicious."
        
        print(f"\nTest Input:")
        print(f"Rating: {test_rating} ⭐")
        print(f"Review: {test_review}")
        
        print("\n🤖 Generating AI analysis...")
        result = get_feedback_analysis(test_rating, test_review)
        
        if result:
            print("\n✅ Analysis generated successfully!")
            print("\n" + "="*60)
            print("USER RESPONSE:")
            print("="*60)
            print(result['user_response'])
            
            print("\n" + "="*60)
            print("INTERNAL SUMMARY:")
            print("="*60)
            print(result['summary'])
            
            print("\n" + "="*60)
            print("RECOMMENDED ACTIONS:")
            print("="*60)
            for i, action in enumerate(result['recommended_actions'], 1):
                print(f"{i}. {action}")
        else:
            print("❌ Failed to generate analysis")
    else:
        print("\n❌ Cannot proceed without working API connection")
    
    print("\n" + "="*60)