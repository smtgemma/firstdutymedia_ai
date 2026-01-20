"""
Bias-Free Service - Schema Definitions
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import List


class BiasBreakdownItem(BaseModel):
    """Individual bias category score (reused from bias_analysis)"""
    category_name: str
    score: int = Field(..., ge=0, le=100, description="0-100 score (higher is better/less biased)")


class BiasMetadata(BaseModel):
    """Bias analysis metadata from the /analyze endpoint"""
    analysis_summary: str = Field(..., description="Summary of detected biases")
    bias_breakdown: List[BiasBreakdownItem] = Field(..., description="Detailed breakdown by category")
    bias_type: str = Field(..., description="Low Bias, Moderate Bias, or High Bias")
    detected_bias_count: int = Field(..., description="Number of bias categories detected")
    overall_seev_score: int = Field(..., ge=0, le=100, description="Overall SEEV score (0-100)")
    title: str = Field(..., description="Analysis session title")
    
    class Config:
        json_schema_extra = {
            "example": {
                "analysis_summary": "The text contains loaded language and makes unsupported claims...",
                "bias_breakdown": [
                    {"category_name": "Source Attribution Bias", "score": 65},
                    {"category_name": "Loaded Language / Labeling Bias", "score": 35}
                ],
                "bias_type": "Moderate Bias",
                "detected_bias_count": 12,
                "overall_seev_score": 45,
                "title": "Job Posting Analysis - Developer Role"
            }
        }


class BiasFreeRequest(BaseModel):
    """Request model for bias removal"""
    text: str = Field(..., description="Original text containing biases")
    bias_metadata: BiasMetadata = Field(..., description="Bias analysis metadata from /analyze endpoint")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Looking for a young, energetic rockstar developer who can work long hours...",
                "bias_metadata": {
                    "analysis_summary": "Contains age bias and loaded language suggesting ageism",
                    "bias_breakdown": [
                        {"category_name": "Age Bias", "score": 25},
                        {"category_name": "Loaded Language / Labeling Bias", "score": 35}
                    ],
                    "bias_type": "Moderate Bias",
                    "detected_bias_count": 2,
                    "overall_seev_score": 45,
                    "title": "Job Posting - Developer Role"
                }
            }
        }


class BiasFreeResponse(BaseModel):
    """Response model for bias removal"""
    bias_free_text: str = Field(..., description="Rewritten text with biases removed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "bias_free_text": "Seeking a motivated software developer with strong problem-solving skills and experience in modern development practices."
            }
        }


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    openai_configured: bool
