"""Utility functions"""
import logging


def setup_logging() -> None:
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def validate_repo_format(repo: str) -> bool:
    """
    Validate that repo string is in correct 'owner/repo' format
    
    Args:
        repo: Repository string to validate
        
    Returns:
        True if valid format
    """
    parts = repo.split('/')
    return len(parts) == 2 and all(part.strip() for part in parts)


