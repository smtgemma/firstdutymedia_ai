from pydantic import BaseModel
from typing import Optional


class ExtractionResponse(BaseModel):
    """
    Schema for text extraction response
    """
    text: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "This is the extracted text from the document"
            }
        }


class HealthResponse(BaseModel):
    """
    Schema for health check response
    """
    status: str
    tesseract: Optional[str] = None
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "tesseract": "available"
            }
        }


class ErrorResponse(BaseModel):
    """
    Schema for error response
    """
    detail: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Error message here"
            }
        }