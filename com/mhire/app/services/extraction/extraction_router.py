from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from com.mhire.app.services.extraction.extraction import ExtractionService
from com.mhire.app.services.extraction.extraction_schema import (
    ExtractionResponse, 
    HealthResponse, 
    ErrorResponse
)

# Create router for extraction endpoints
router = APIRouter(
    prefix="/extraction",
    tags=["extraction"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the OCR service and Tesseract are available"
)
async def health_check():
    """
    Health check endpoint to verify Tesseract OCR is working
    """
    status, message = ExtractionService.check_tesseract_health()
    
    if status == "healthy":
        return HealthResponse(status=status, tesseract=message)
    else:
        return HealthResponse(status=status, error=message)


@router.post(
    "/extract",
    response_model=ExtractionResponse,
    summary="Extract Text",
    description="Extract text from uploaded image or PDF file"
)
async def extract_text(
    file: UploadFile = File(..., description="Image or PDF file to extract text from")
):
    """
    Extract text from uploaded image or PDF.
    
    Supports:
    - Images: JPG, JPEG, PNG, WEBP, TIFF, BMP, GIF
    - Documents: PDF
    
    Returns:
    - text: The extracted text from the document
    """
    
    try:
        # Read file content
        contents = await file.read()
        
        # Extract text using the service
        extracted_text = ExtractionService.extract_text(
            file_content=contents,
            content_type=file.content_type,
            filename=file.filename
        )
        
        return ExtractionResponse(text=extracted_text)
        
    except ValueError as ve:
        # File type validation error
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )
    except Exception as e:
        # General extraction error
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )