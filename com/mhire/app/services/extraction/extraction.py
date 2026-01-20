from PIL import Image
import pytesseract
import pymupdf
import io
from typing import Tuple


class ExtractionService:
    """
    Service class for handling text extraction from images and PDFs
    """
    
    @staticmethod
    def detect_file_type(content_type: str, filename: str) -> str:
        """
        Detect if the uploaded file is a PDF or image
        
        Args:
            content_type: MIME type of the file
            filename: Name of the uploaded file
            
        Returns:
            str: 'pdf' or 'image'
            
        Raises:
            ValueError: If file type is not supported
        """
        content_type_lower = content_type.lower() if content_type else ""
        filename_lower = filename.lower() if filename else ""
        
        # Check if it's a PDF
        if content_type_lower == "application/pdf" or filename_lower.endswith(".pdf"):
            return "pdf"
        
        # Check if it's an image
        image_types = ["image/jpeg", "image/png", "image/jpg", "image/webp", "image/tiff"]
        image_extensions = [".jpg", ".jpeg", ".png", ".webp", ".tiff", ".bmp", ".gif"]
        
        if any(img_type in content_type_lower for img_type in image_types) or \
           any(filename_lower.endswith(ext) for ext in image_extensions):
            return "image"
        
        raise ValueError("Unsupported file type. Please upload an image (JPG, PNG, etc.) or PDF file.")
    
    @staticmethod
    def extract_text_from_pdf(pdf_bytes: bytes) -> str:
        """
        Extract text from PDF using PyMuPDF (fitz)
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            str: Extracted text from all pages
            
        Raises:
            Exception: If PDF extraction fails
        """
        try:
            # Open PDF from bytes
            pdf_document = pymupdf.open(stream=pdf_bytes, filetype="pdf")
            
            # Extract text from all pages
            text = ""
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                page_text = page.get_text()
                text += page_text
                
                # Add page separator for multi-page PDFs
                if page_num < pdf_document.page_count - 1:
                    text += "\n\n"
            
            pdf_document.close()
            
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    @staticmethod
    def extract_text_from_image(image_bytes: bytes, lang: str = "eng") -> str:
        """
        Extract text from image using Tesseract OCR
        
        Args:
            image_bytes: Image file content as bytes
            lang: Language code for OCR (default: 'eng')
            
        Returns:
            str: Extracted text from image
            
        Raises:
            Exception: If image extraction fails
        """
        try:
            # Open image from bytes
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert RGBA to RGB if necessary
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            
            # Extract text using pytesseract
            text = pytesseract.image_to_string(image, lang=lang)
            
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from image: {str(e)}")
    
    @staticmethod
    def extract_text(file_content: bytes, content_type: str, filename: str) -> str:
        """
        Main method to extract text from either PDF or image
        
        Args:
            file_content: File content as bytes
            content_type: MIME type of the file
            filename: Name of the uploaded file
            
        Returns:
            str: Extracted text
            
        Raises:
            ValueError: If file type is not supported
            Exception: If extraction fails
        """
        # Detect file type
        file_type = ExtractionService.detect_file_type(content_type, filename)
        
        # Extract text based on file type
        if file_type == "pdf":
            text = ExtractionService.extract_text_from_pdf(file_content)
        else:
            text = ExtractionService.extract_text_from_image(file_content)
        
        return text.strip()
    
    @staticmethod
    def check_tesseract_health() -> Tuple[str, str]:
        """
        Check if Tesseract OCR is installed and working
        
        Returns:
            Tuple[str, str]: (status, message)
        """
        try:
            version = pytesseract.get_tesseract_version()
            return "healthy", "available"
        except Exception as e:
            return "unhealthy", str(e)