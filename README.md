# OCR & Bias Removal API

A robust FastAPI application that provides services for removing bias from text using GPT-4 and extracting text from documents (OCR).

## 🚀 Features

- **Bias Removal (Primary)**: Advanced bias neutralization engine that accepts detailed bias scores and metadata to rewrite text into a neutral, professional tone.
- **Bias Removal (Secondary)**: Alternative endpoint for bias removal functionality.
- **OCR / Text Extraction**: Extract text from images and PDF documents using Tesseract OCR and PyMuPDF.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.8+**
- **Tesseract OCR**: Required for text extraction from images.
  - [Windows Installer](https://github.com/UB-Mannheim/tesseract/wiki) (Add Tesseract to your system PATH)
  - Linux: `sudo apt-get install tesseract-ocr`
  - macOS: `brew install tesseract`

## 🛠️ Installation

1.  **Clone the repository**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create a virtual environment**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # Linux/Mac
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**
    Create a `.env` file in the root directory (or ensure your config reads from system env vars) and add your OpenAI API key:
    ```env
    OPENAI_API_KEY=sk-your-api-key-here
    ```

## 🏃‍♂️ Running the Application

Start the server using Uvicorn:

```bash
uvicorn com.mhire.app.main:app --reload
```

The API will be available at: `http://localhost:8000`

## 📚 API Documentation

Once the server is running, you can access the interactive API documentation:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🔌 Endpoints

### 1. Remove Bias (Primary)
**Endpoint**: `POST /api/v2/remove-bias`

Removes bias from text based on provided scores and detected bias types.

**Request Example**:
```json
{
  "text": "Looking for a young, energetic rockstar developer who can work long hours...",
  "score": 55,
  "flags": "yellow",
  "bias_types": [
    {
      "code": "B1",
      "label": "Age Bias"
    },
    {
      "code": "B12",
      "label": "Work Culture Bias"
    }
  ],
  "explanation": "The text contains implicit age bias and exclusionary work culture references."
}
```

**Response Example**:
```json
{
  "bias_free_text": "Seeking a motivated software developer with strong problem-solving skills and experience in modern development practices."
}
```

### 2. Remove Bias (Secondary)
**Endpoint**: `POST /api/v1/remove-bias`

Alternative endpoint for bias removal operations.

### 3. Extract Text (OCR)
**Endpoint**: `POST /extraction/extract`

Extracts text from uploaded images or PDF files.
- **Input**: File upload (Multipart/form-data)
- **Output**: Extracted text content

## 🏥 Health Checks

- **API Root**: `GET /`
- **General Health**: `GET /health`
- **Bias Service Health**: `GET /api/v2/bias-free/health`

## 🐳 Running with Docker

You can also run the application using Docker and Docker Compose. This setup includes an Nginx reverse proxy.

1.  **Build and Run**
    ```bash
    docker-compose up --build -d
    ```

2.  **Access the Application**
    The application will be served via Nginx at:
    - **API Root**: `http://localhost:8022`
    - **Swagger UI**: [http://localhost:8022/docs](http://localhost:8022/docs)

    *Note: The application runs on port `8022` when used with Docker Compose, rather than `8000`.*

3.  **Stop the Application**
    ```bash
    docker-compose down
    ```

## 🤝 Project Structure

```
com/mhire/app/
├── main.py                  # Application entry point
├── config/                  # Configuration settings
└── services/
    ├── bias_free_different/ # Primary Bias Removal Service (V2)
    ├── bias_free/           # Secondary Bias Removal Service (V1)
    └── extraction/          # OCR & Text Extraction Service

Dockerfile                   # Docker build instructions
docker-compose.yml           # Docker Compose configuration
nginx/                       # Nginx configuration
```
