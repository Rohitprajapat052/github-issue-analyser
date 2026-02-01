"""Groq LLM client for analyzing GitHub issues"""
import logging
import os
from typing import List, Dict, Any
from groq import Groq

logger = logging.getLogger(__name__)

# Initialize Groq client
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    logger.warning("GROQ_API_KEY not found in environment variables")

client = Groq(api_key=groq_api_key) if groq_api_key else None


def analyze_issues(issues: List[Dict[str, Any]], user_prompt: str) -> Dict[str, Any]:
    """
    Analyze GitHub issues using Groq LLM
    
    Args:
        issues: List of issue dictionaries
        user_prompt: User's analysis request
        
    Returns:
        Dictionary with 'success', 'analysis', and 'error' keys
    """
    if not client:
        error_msg = "Groq API key not configured"
        logger.error(error_msg)
        return {
            "success": False,
            "analysis": "",
            "error": error_msg
        }
    
    try:
        # Handle context limits - if too many issues, limit to most recent 50
        if len(issues) > 100:
            logger.warning(f"Too many issues ({len(issues)}). Limiting to 50 most recent")
            issues = issues[:50]
        
        # Format issues for LLM
        issues_text = format_issues_for_llm(issues)
        
        # Prepare messages
        system_prompt = (
            "You are a GitHub issue analyzer. Analyze the provided issues "
            "and respond to the user's request clearly and concisely. "
            "Focus on actionable insights and patterns."
        )
        
        user_message = f"{user_prompt}\n\nIssues to analyze:\n\n{issues_text}"
        
        logger.info(f"Sending {len(issues)} issues to Groq for analysis")
        
        # Call Groq API with retry logic
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.7,
                    max_tokens=2048,
                    timeout=60
                )
                
                analysis = response.choices[0].message.content
                logger.info("Successfully received Groq analysis")
                
                return {
                    "success": True,
                    "analysis": analysis,
                    "error": None
                }
                
            except Exception as e:
                logger.warning(f"Groq attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                continue
        
    except Exception as e:
        error_msg = f"LLM analysis error: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "analysis": "",
            "error": error_msg
        }


def format_issues_for_llm(issues: List[Dict[str, Any]]) -> str:
    """
    Format issues into a readable text format for LLM
    
    Args:
        issues: List of issue dictionaries
        
    Returns:
        Formatted string of issues
    """
    formatted_parts = []
    
    for idx, issue in enumerate(issues, 1):
        title = issue.get('title', 'No title')
        body = issue.get('body', '')
        created_at = issue.get('created_at', 'Unknown date')
        url = issue.get('html_url', '')
        
        # Truncate long bodies to avoid context overflow
        if body and len(body) > 500:
            body = body[:500] + "..."
        
        issue_text = f"""Issue #{idx}:
Title: {title}
Created: {created_at}
URL: {url}
Description: {body if body else "No description provided"}
---"""
        
        formatted_parts.append(issue_text)
    
    return "\n\n".join(formatted_parts)