import os
import shutil
import logging
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from paddleocr import PaddleOCR

# Import from your compiled wheel
from ssm_logic import parse_ssm_content

# --- 1. CONFIGURATION & LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MDT-SVC-OCR")

API_KEY_NAME = "X-API-KEY"
# Best practice: Fetch from env, but fail if not set in production
API_KEY = os.getenv("API_KEY", "default_secret_key_123")

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# --- 2. SECURITY ---
async def get_api_key(header_value: str = Depends(api_key_header)):
    if header_value == API_KEY:
        return header_value
    logger.warning(f"Unauthorized access attempt with key: {header_value}")
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Access Denied: Invalid API Key"
    )

app = FastAPI(title="MDT SVC OCR")

# --- 3. OCR INITIALIZATION ---
# Initialize once globally to avoid memory leaks
ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False, show_log=False)

@app.post("/extract-ssm-file")
async def extract_ssm_file(
    file: UploadFile = File(...), 
    token: str = Depends(get_api_key)
):
    # Use a secure temp file to avoid "Permission Denied" and filename collisions
    # suffix ensures PaddleOCR recognizes the file type (jpg/png/pdf)
    suffix = os.path.splitext(file.filename)[1]
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        temp_path = tmp.name
        try:
            # Write upload to temp file
            shutil.copyfileobj(file.file, tmp)
            tmp.flush() # Ensure all data is written to disk
            tmp.close() # Close handle so PaddleOCR can open it on Windows

            logger.info(f"Processing file: {file.filename}")
            
            # Perform OCR
            result = ocr.ocr(temp_path, cls=True)
            
            # Extract text safely
            raw_lines = []
            if result and result[0]:
                raw_lines = [res[1][0] for res in result[0]]

            # Call your compiled logic
            summary = parse_ssm_content(raw_lines)
            
            return {
                "success": True, 
                "summary": summary,
                "filename": file.filename
            }

        except Exception as e:
            logger.error(f"OCR Error: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal processing error")
        
        finally:
            # Clean up: the file is removed even if the code crashes
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception as cleanup_error:
                    logger.error(f"Failed to delete temp file: {cleanup_error}")