"""
SEEV Bias Analysis - Schema Definitions
All Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import List


class AnalyzeRequest(BaseModel):
    """Request model for bias analysis"""
    text: str = Field(..., description="Text content to analyze")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "This groundbreaking study proves our revolutionary approach..."
            }
        }


class BiasBreakdownItem(BaseModel):
    """Individual bias category score"""
    category_name: str
    score: int = Field(..., ge=0, le=100, description="0-100 score (higher is better/less biased)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "category_name": "Source Attribution Bias",
                "score": 65
            }
        }


class AnalyzeResponse(BaseModel):
    """Response model for bias analysis"""
    overall_seev_score: int = Field(..., ge=0, le=100, description="Overall SEEV score (0-100)")
    title: str = Field(..., description="Session title/name based on the analyzed text")
    bias_breakdown: List[BiasBreakdownItem] = Field(..., description="Detailed breakdown by category")
    bias_type: str = Field(..., description="Low Bias, Moderate Bias, or High Bias")
    analysis_summary: str = Field(..., description="Brief summary of main bias issues")
    detected_bias_count: int = Field(..., description="Number of bias categories detected")
    
    class Config:
        json_schema_extra = {
            "example": {
                "overall_seev_score": 45,
                "title": "Job Posting Analysis - Developer Role",
                "bias_breakdown": [
                    {"category_name": "Source Attribution Bias", "score": 65},
                    {"category_name": "Loaded Language / Labeling Bias", "score": 35}
                ],
                "bias_type": "Moderate Bias",
                "analysis_summary": "The text contains loaded language and makes unsupported claims...",
                "detected_bias_count": 12
            }
        }


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    openai_configured: bool