"""
Bias-Free Service - API Router
Defines all API endpoints for bias removal
"""

from fastapi import APIRouter, HTTPException
from com.mhire.app.config.config import Config
from com.mhire.app.services.bias_free_different.bias_free_different_schema import (
    BiasFreeRequest,
    BiasFreeResponse,
    HealthCheckResponse
)
from com.mhire.app.services.bias_free_different.bias_free_different import BiasFreeService


# Initialize router
router = APIRouter(
    prefix="/api/v2",
    tags=["Bias Removal Primary"],
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
async def remove_bias_different(request: BiasFreeRequest):
    """
    Remove biases from text using GPT-4 based on client's bias analysis.
    
    **Input:**
    - text: The original text containing biases
    - score: Bias score (0-33=High Bias, 34-66=Moderate Bias, 67-100=Low Bias)
    - flags: Flag color indicator (e.g., red, yellow, green)
    - bias_types: List of detected bias type codes
    - explanation: Explanation of detected biases
    
    **Output:**
    - bias_free_text: Rewritten text with biases removed
    
    **Example Request:**
    ```json
    {
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
    ```
    
    **Workflow:**
    1. Receive bias analysis from client's API
    2. Call this endpoint with the text and bias information
    3. Receive bias-free rewritten text
    """
    try:
        result = await bias_free_service.remove_bias(
            request.text,
            request.score,
            request.flags,
            request.bias_types,
            request.explanation
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
async def health_check_different():
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
