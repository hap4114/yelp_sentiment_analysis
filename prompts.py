"""
Prompt templates for the Restaurant Feedback System.
Contains three main prompt types:
1. User Response - Customer-facing reply
2. Summary - Internal summary for admin
3. Recommended Actions - Actionable steps for management
"""

def get_user_response_prompt(rating: int, review: str) -> str:
    """
    Generate prompt for user-facing response.
    
    Args:
        rating (int): Star rating (1-5)
        review (str): User's review text
        
    Returns:
        str: Formatted prompt for LLM
    """
    
    rating_context = {
        1: "very negative",
        2: "negative",
        3: "neutral/mixed",
        4: "positive",
        5: "very positive"
    }
    
    sentiment = rating_context.get(rating, "neutral")
    
    prompt = f"""You are a professional restaurant manager responding to customer feedback.

Customer Rating: {rating}/5 stars ({sentiment})
Customer Review: "{review}"

Write a warm, professional response to this customer. Follow these guidelines:

1. For POSITIVE feedback (4-5 stars):
   - Thank them genuinely
   - Highlight what they loved
   - Invite them back
   - Keep it warm but not overly long

2. For NEUTRAL feedback (3 stars):
   - Thank them for honest feedback
   - Acknowledge their experience
   - Show you're working on improvements
   - Invite them to give you another chance

3. For NEGATIVE feedback (1-2 stars):
   - Apologize sincerely
   - Acknowledge their specific concerns
   - Explain what you'll do differently
   - Offer to make it right (if appropriate)

Requirements:
- Be authentic and human, not corporate
- Keep response under 100 words
- Address specific points from their review
- Show empathy and care
- Don't make promises you can't keep
- Match the tone to their sentiment

Write ONLY the response text, nothing else."""

    return prompt


def get_summary_prompt(rating: int, review: str) -> str:
    """
    Generate prompt for internal summary.
    
    Args:
        rating (int): Star rating (1-5)
        review (str): User's review text
        
    Returns:
        str: Formatted prompt for LLM
    """
    
    prompt = f"""You are analyzing customer feedback for internal restaurant management.

Rating: {rating}/5 stars
Review: "{review}"

Create a concise internal summary (2-3 sentences) that captures:
1. Main sentiment and key points
2. Specific issues or praise mentioned
3. Severity/urgency level

Be factual and objective. Focus on actionable insights.

Write ONLY the summary, nothing else."""

    return prompt


def get_actions_prompt(rating: int, review: str, summary: str) -> str:
    """
    Generate prompt for recommended actions.
    
    Args:
        rating (int): Star rating (1-5)
        review (str): User's review text
        summary (str): Internal summary
        
    Returns:
        str: Formatted prompt for LLM
    """
    
    prompt = f"""You are a restaurant operations consultant. Based on this feedback, recommend specific actions.

Rating: {rating}/5 stars
Review: "{review}"
Summary: {summary}

Generate 3-5 SPECIFIC, ACTIONABLE recommendations for management.

Guidelines:
- Be specific (not vague like "improve service")
- Prioritize by impact and urgency
- Make them measurable when possible
- Consider quick wins vs long-term improvements
- Address root causes, not just symptoms

Format each action as a single clear sentence.
Number them 1-5.

Example format:
1. Train front-of-house staff on greeting protocols within 48 hours
2. Conduct quality check on pasta dishes during next 3 dinner services
3. Review and update menu descriptions for clarity

Write ONLY the numbered action list, nothing else."""

    return prompt


# Testing
if __name__ == "__main__":
    print("="*60)
    print("PROMPT TEMPLATES - EXAMPLES")
    print("="*60)
    
    # Test data
    test_rating = 2
    test_review = "Food was cold and service was slow. Waited 45 minutes for our order."
    test_summary = "Negative experience due to cold food and excessive wait time (45 min). Service quality issues."
    
    print("\n1. USER RESPONSE PROMPT:")
    print("-"*60)
    print(get_user_response_prompt(test_rating, test_review))
    
    print("\n\n2. SUMMARY PROMPT:")
    print("-"*60)
    print(get_summary_prompt(test_rating, test_review))
    
    print("\n\n3. ACTIONS PROMPT:")
    print("-"*60)
    print(get_actions_prompt(test_rating, test_review, test_summary))
    
    print("\n" + "="*60)