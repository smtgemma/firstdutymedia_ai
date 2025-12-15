"""
SEEV Bias Analysis - API Router
Defines all API endpoints for bias analysis
"""

from fastapi import APIRouter, HTTPException
import openai
from com.mhire.app.config.config import Config
from com.mhire.app.services.bias_analysis.bias_analysis_schema import (
    AnalyzeRequest,
    AnalyzeResponse,
    HealthCheckResponse
)
from com.mhire.app.services.bias_analysis.bias_analysis import BiasAnalysisService


# Initialize router
router = APIRouter(
    prefix="/api/v1",
    tags=["Bias Analysis"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

# Initialize service
bias_service = BiasAnalysisService()


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Analyze text for bias",
    description="Analyzes input text across 25 bias categories and returns detailed scoring"
)
async def analyze_text(request: AnalyzeRequest):
    """
    Analyze text for bias across 25 categories using GPT-4.
    
    **Input:**
    - text: The content to analyze
    
    **Output:**
    - overall_seev_score: Overall bias score (0-100, higher is better)
    - bias_breakdown: Detailed scores for each detected bias category
    - bias_type: Classification (Low/Moderate/High Bias)
    - analysis_summary: Brief explanation of main biases found
    - detected_bias_count: Number of bias categories with concerns
    
    **Example Request:**
    ```json
    {
        "text": "This groundbreaking study proves our revolutionary approach..."
    }
    ```
    """
    try:
        result = await bias_service.analyze_text(request.text)
        return AnalyzeResponse(**result)
    
    except HTTPException:
        # Re-raise HTTP exceptions from service
        raise
    
    except Exception as e:
        # Catch any unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during analysis: {str(e)}"
        )


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health check",
    description="Check if the API and OpenAI integration are working correctly"
)
async def health_check():
    """
    Health check endpoint to verify API status.
    
    **Returns:**
    - status: "healthy" if API is running
    - openai_configured: True if OpenAI API key is configured
    """
    config = Config()
    
    return HealthCheckResponse(
        status="healthy",
        openai_configured=bool(config.openai_api_key)
    )