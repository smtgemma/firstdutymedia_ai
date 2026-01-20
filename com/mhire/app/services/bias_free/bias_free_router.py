"""
Bias-Free Service - API Router
Defines all API endpoints for bias removal
"""

from fastapi import APIRouter, HTTPException
from com.mhire.app.config.config import Config
from com.mhire.app.services.bias_free.bias_free_schema import (
    BiasFreeRequest,
    BiasFreeResponse,
    HealthCheckResponse
)
from com.mhire.app.services.bias_free.bias_free import BiasFreeService


# Initialize router
router = APIRouter(
    prefix="/api/v1",
    tags=["Bias Removal Secondary"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

# Initialize service
bias_free_service = BiasFreeService()


@router.post(
    "/remove-bias",
    response_model=BiasFreeResponse,
    summary="Remove bias from text",
    description="Rewrites text to remove detected biases based on bias analysis metadata"
)
async def remove_bias(request: BiasFreeRequest):
    """
    Remove biases from text using GPT-4 based on bias analysis metadata.
    
    **Input:**
    - text: The original text containing biases
    - bias_metadata: Complete bias analysis metadata from /analyze endpoint
    
    **Output:**
    - bias_free_text: Rewritten text with biases removed
    
    **Example Request:**
    ```json
    {
        "text": "Looking for a young, energetic rockstar developer...",
        "bias_metadata": {
            "overall_seev_score": 45,
            "bias_type": "Moderate Bias",
            "detected_bias_count": 2,
            "analysis_summary": "Contains age bias and loaded language",
            "bias_breakdown": [
                {"category_name": "Age Bias", "score": 25},
                {"category_name": "Loaded Language / Labeling Bias", "score": 35}
            ],
            "title": "Job Posting - Developer Role"
        }
    }
    ```
    
    **Workflow:**
    1. First call `/api/v1/analyze` with your text to get bias analysis
    2. Then call this endpoint with the original text + bias metadata
    3. Receive bias-free rewritten text
    """
    try:
        result = await bias_free_service.remove_bias(
            request.text, 
            request.bias_metadata
        )
        return BiasFreeResponse(**result)
    
    except HTTPException:
        # Re-raise HTTP exceptions from service
        raise
    
    except Exception as e:
        # Catch any unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during bias removal: {str(e)}"
        )


@router.get(
    "/bias-free/health",
    response_model=HealthCheckResponse,
    summary="Health check",
    description="Check if the bias-free API and OpenAI integration are working correctly"
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
