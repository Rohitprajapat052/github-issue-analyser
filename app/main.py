"""FastAPI application for GitHub Issue Analyzer"""
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

from app.models import (
    ScanRequest, ScanResponse,
    AnalyzeRequest, AnalyzeResponse,
    ErrorResponse
)
from app.database import init_db, cache_issues, get_cached_issues, repo_exists_in_cache
from app.github_client import fetch_all_issues
from app.llm_client import analyze_issues
from app.utils import setup_logging, validate_repo_format

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app"""
    # Startup
    logger.info("Starting GitHub Issue Analyzer...")
    init_db()
    logger.info("Application ready")
    yield
    # Shutdown
    logger.info("Shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="GitHub Issue Analyzer",
    description="Analyze GitHub repository issues using LLM",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "GitHub Issue Analyzer",
        "version": "1.0.0"
    }


@app.post("/scan", response_model=ScanResponse)
async def scan_repo(request: ScanRequest):
    """
    Fetch all open issues from a GitHub repository and cache them locally
    
    - **repo**: GitHub repository in format 'owner/repository-name'
    """
    repo = request.repo.strip()
    
    # Validate repo format
    if not validate_repo_format(repo):
        logger.error(f"Invalid repo format: {repo}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid repository format",
                "details": "Repository must be in format 'owner/repository-name'"
            }
        )
    
    logger.info(f"Scanning repository: {repo}")
    
    # Fetch issues from GitHub
    result = fetch_all_issues(repo)
    
    if not result["success"]:
        logger.error(f"Failed to fetch issues: {result['error']}")
        status_code = 404 if "not found" in result["error"].lower() else 500
        raise HTTPException(
            status_code=status_code,
            detail={
                "error": result["error"],
                "details": "Failed to fetch issues from GitHub API"
            }
        )
    
    issues = result["issues"]
    issues_count = len(issues)
    
    # Cache issues in database
    cached_successfully = cache_issues(repo, issues)
    
    if not cached_successfully:
        logger.error(f"Failed to cache issues for repo: {repo}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to cache issues",
                "details": "Issues were fetched but could not be saved to database"
            }
        )
    
    logger.info(f"Successfully scanned and cached {issues_count} issues for repo: {repo}")
    
    return ScanResponse(
        repo=repo,
        issues_fetched=issues_count,
        cached_successfully=True
    )


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_repo(request: AnalyzeRequest):
    """
    Analyze cached issues for a repository using LLM
    
    - **repo**: GitHub repository in format 'owner/repository-name'
    - **prompt**: Natural language prompt describing what analysis you want
    """
    repo = request.repo.strip()
    user_prompt = request.prompt.strip()
    
    # Validate repo format
    if not validate_repo_format(repo):
        logger.error(f"Invalid repo format: {repo}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid repository format",
                "details": "Repository must be in format 'owner/repository-name'"
            }
        )
    
    # Validate prompt
    if not user_prompt:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Empty prompt",
                "details": "Analysis prompt cannot be empty"
            }
        )
    
    # Check if repo has been scanned
    if not repo_exists_in_cache(repo):
        logger.error(f"Repo not scanned: {repo}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Repository not yet scanned",
                "details": f"Please scan the repository '{repo}' first using the /scan endpoint"
            }
        )
    
    logger.info(f"Analyzing repository: {repo}")
    
    # Get cached issues
    issues = get_cached_issues(repo)
    
    if issues is None:
        logger.error(f"Failed to retrieve cached issues for repo: {repo}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to retrieve cached issues",
                "details": "Issues exist but could not be loaded from database"
            }
        )
    
    if len(issues) == 0:
        return AnalyzeResponse(
            analysis=f"The repository '{repo}' has no open issues to analyze."
        )
    
    # Analyze with LLM
    result = analyze_issues(issues, user_prompt)
    
    if not result["success"]:
        logger.error(f"LLM analysis failed: {result['error']}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": result["error"],
                "details": "Failed to analyze issues with LLM"
            }
        )
    
    logger.info(f"Successfully analyzed {len(issues)} issues for repo: {repo}")
    
    return AnalyzeResponse(analysis=result["analysis"])


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )