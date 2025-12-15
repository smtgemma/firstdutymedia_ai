from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from com.mhire.app.services.document_processing.document_extract_router import router as document_extraction_router
from com.mhire.app.services.bias_analysis.bias_analysis_router import router as bias_router

app = FastAPI(
    title="SEEV Bias Dashboard API",
    description="AI-powered bias detection and analysis across 25 categories",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(document_extraction_router)
app.include_router(bias_router)


# Health check endpoint

@app.get("/")  # Default JSONResponse
async def root():
    return {"message": "Hello"}  # ✓ Dict for JSON



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable auto-reload for development
    )