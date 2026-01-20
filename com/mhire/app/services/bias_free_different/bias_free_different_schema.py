"""
Bias-Free Service - Schema Definitions
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import List


class BiasType(BaseModel):
    """Individual bias type with code and label"""
    code: str = Field(..., description="Bias type code (e.g., B1, B7, B12)")
    label: str = Field(..., description="Bias type label (e.g., Bias Type 1)")


class BiasFreeRequest(BaseModel):
    """Request model for bias removal using client API format"""
    text: str = Field(..., description="Original text containing biases")
    score: int = Field(..., ge=0, le=100, description="Bias score: 0-33=High Bias, 34-66=Moderate Bias, 67-100=Low Bias")
    flags: str = Field(..., description="Flag color indicator (e.g., red, yellow, green)")
    bias_types: List[BiasType] = Field(..., description="List of detected bias types with codes")
    explanation: str = Field(..., description="Explanation of detected biases (similar to analysis_summary)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Looking for a young, energetic rockstar developer who can work long hours...",
                "score": 72,
                "flags": "yellow",
                "bias_types": [
                    {"code": "B1", "label": "Bias Type 1"},
                    {"code": "B7", "label": "Bias Type 7"},
                    {"code": "B12", "label": "Bias Type 12"}
                ],
                "explanation": "This is a placeholder explanation generated for demonstration purposes only. No real bias analysis has been performed."
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
