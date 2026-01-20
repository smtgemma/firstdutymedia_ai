from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from com.mhire.app.services.extraction.extraction_router import router as extraction_router
from com.mhire.app.services.bias_free.bias_free_router import router as bias_free_router
from com.mhire.app.services.bias_free_different.bias_free_different_router import router as bias_free_different_router
# Create FastAPI application
app = FastAPI(
    title="OCR Text Extraction API",
    description="Extract text from images and PDFs using Tesseract OCR and PyMuPDF",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS (optional - adjust as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(extraction_router)
app.include_router(bias_free_router)
app.include_router(bias_free_different_router)

@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "OCR Text Extraction API",
        "version": "1.0.0",
        "endpoints": {
            "/docs": "Swagger UI Documentation",
            "/redoc": "ReDoc Documentation",
            "/extraction/health": "GET - Health check for OCR service",
            "/extraction/extract": "POST - Extract text from image or PDF"
                    }
    }


@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """
    Run on application startup
    """
    print("🚀 OCR Text Extraction API is starting...")
    print("📝 API Documentation available at: /docs")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown
    """
    print("👋 OCR Text Extraction API is shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "com.mhire.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )