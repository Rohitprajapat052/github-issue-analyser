"""GitHub API client for fetching repository issues"""
import requests
import logging
import os
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"


def fetch_all_issues(repo: str) -> Dict[str, Any]:
    """
    Fetch all open issues from a GitHub repository with pagination
    
    Args:
        repo: Repository name in format 'owner/repo'
        
    Returns:
        Dictionary with 'success', 'issues', and 'error' keys
    """
    issues: List[Dict[str, Any]] = []
    page = 1
    per_page = 100  # GitHub's maximum per page
    
    # Prepare headers
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-Issue-Analyzer"
    }
    
    # Add GitHub token if available (increases rate limit)
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"token {github_token}"
        logger.info("Using GitHub token for authentication")
    
    try:
        while True:
            url = f"{GITHUB_API_BASE}/repos/{repo}/issues"
            params = {
                "state": "open",
                "per_page": per_page,
                "page": page
            }
            
            logger.info(f"Fetching page {page} for repo: {repo}")
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            # Handle rate limiting
            if response.status_code == 403:
                error_msg = "GitHub API rate limit exceeded"
                if not github_token:
                    error_msg += ". Add GITHUB_TOKEN to .env for higher limits"
                logger.error(error_msg)
                return {
                    "success": False,
                    "issues": [],
                    "error": error_msg
                }
            
            # Handle repository not found
            if response.status_code == 404:
                error_msg = f"Repository '{repo}' not found"
                logger.error(error_msg)
                return {
                    "success": False,
                    "issues": [],
                    "error": error_msg
                }
            
            # Handle other errors
            if response.status_code != 200:
                error_msg = f"GitHub API error: {response.status_code}"
                logger.error(f"{error_msg} - {response.text}")
                return {
                    "success": False,
                    "issues": [],
                    "error": error_msg
                }
            
            page_issues = response.json()
            
            # Break if no more issues
            if not page_issues:
                logger.info(f"No more issues found. Total pages fetched: {page - 1}")
                break
            
            # Filter out pull requests (GitHub includes them in issues endpoint)
            actual_issues = [
                issue for issue in page_issues 
                if 'pull_request' not in issue
            ]
            
            issues.extend(actual_issues)
            logger.info(f"Fetched {len(actual_issues)} issues from page {page}")
            
            # If we got fewer than per_page items, we're done
            if len(page_issues) < per_page:
                break
            
            page += 1
        
        logger.info(f"Successfully fetched {len(issues)} total issues for repo: {repo}")
        return {
            "success": True,
            "issues": issues,
            "error": None
        }
        
    except requests.exceptions.Timeout:
        error_msg = "GitHub API request timed out"
        logger.error(error_msg)
        return {
            "success": False,
            "issues": [],
            "error": error_msg
        }
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error while fetching issues: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "issues": [],
            "error": error_msg
        }
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "issues": [],
            "error": error_msg
        }