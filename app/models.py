"""Pydantic models for request/response validation"""
from typing import Optional
from pydantic import BaseModel, Field


class ScanRequest(BaseModel):
    """Request model for /scan endpoint"""
    repo: str = Field(
        ..., 
        description="GitHub repository in format 'owner/repo'",
        examples=["microsoft/vscode-python"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "repo": "microsoft/vscode-python"
            }
        }


class ScanResponse(BaseModel):
    """Response model for /scan endpoint"""
    repo: str
    issues_fetched: int
    cached_successfully: bool


class AnalyzeRequest(BaseModel):
    """Request model for /analyze endpoint"""
    repo: str = Field(
        ...,
        description="GitHub repository in format 'owner/repo'",
        examples=["microsoft/vscode-python"]
    )
    prompt: str = Field(
        ...,
        description="Natural language prompt for analysis",
        examples=["What are the top 3 most common issue types?"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "repo": "microsoft/vscode-python",
                "prompt": "Summarize the main themes and recommend what to fix first"
            }
        }


class AnalyzeResponse(BaseModel):
    """Response model for /analyze endpoint"""
    analysis: str


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str
    details: Optional[str] = None