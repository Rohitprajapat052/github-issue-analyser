"""SQLite database setup and operations"""
import sqlite3
import logging
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)

DATABASE_PATH = "issues.db"


def init_db() -> None:
    """Initialize the database with required schema"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create issues table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS issues (
                    id INTEGER PRIMARY KEY,
                    repo TEXT NOT NULL,
                    title TEXT NOT NULL,
                    body TEXT,
                    html_url TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index for faster repo lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_repo ON issues(repo)
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")
            
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}")
        raise


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def cache_issues(repo: str, issues: List[Dict[str, Any]]) -> bool:
    """
    Cache GitHub issues in the database
    
    Args:
        repo: Repository name in format 'owner/repo'
        issues: List of issue dictionaries from GitHub API
        
    Returns:
        True if caching was successful
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Delete existing issues for this repo (fresh cache)
            cursor.execute("DELETE FROM issues WHERE repo = ?", (repo,))
            
            # Insert new issues
            for issue in issues:
                cursor.execute("""
                    INSERT INTO issues (id, repo, title, body, html_url, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    issue['id'],
                    repo,
                    issue['title'],
                    issue.get('body') or '',
                    issue['html_url'],
                    issue['created_at']
                ))
            
            conn.commit()
            logger.info(f"Cached {len(issues)} issues for repo: {repo}")
            return True
            
    except sqlite3.Error as e:
        logger.error(f"Error caching issues: {e}")
        return False


def get_cached_issues(repo: str) -> Optional[List[Dict[str, Any]]]:
    """
    Retrieve cached issues for a repository
    
    Args:
        repo: Repository name in format 'owner/repo'
        
    Returns:
        List of issue dictionaries or None if not found
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, repo, title, body, html_url, created_at
                FROM issues
                WHERE repo = ?
                ORDER BY created_at DESC
            """, (repo,))
            
            rows = cursor.fetchall()
            
            if not rows:
                logger.warning(f"No cached issues found for repo: {repo}")
                return None
            
            # Convert to list of dictionaries
            issues = [dict(row) for row in rows]
            logger.info(f"Retrieved {len(issues)} cached issues for repo: {repo}")
            return issues
            
    except sqlite3.Error as e:
        logger.error(f"Error retrieving cached issues: {e}")
        return None


def repo_exists_in_cache(repo: str) -> bool:
    """Check if a repository has been scanned and cached"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM issues WHERE repo = ? LIMIT 1",
                (repo,)
            )
            count = cursor.fetchone()[0]
            return count > 0
            
    except sqlite3.Error as e:
        logger.error(f"Error checking repo existence: {e}")
        return False