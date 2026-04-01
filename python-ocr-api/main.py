import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from paddleocr import PaddleOCR

# Import from your compiled wheel
from ssm_logic import parse_ssm_content

# Security Configuration
API_KEY_NAME = "X-API-KEY"
# Read the key from Environment Variable (or use a fallback for dev)
API_KEY = os.getenv("API_KEY", "default_secret_key_123")

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(header_value: str = Depends(api_key_header)):
    if header_value == API_KEY:
        return header_value
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Access Denied: Invalid API Key"
    )

app = FastAPI(title="MDT SVC OCR")

# Initialize OCR
ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False, show_log=False)

@app.post("/extract-ssm-file")
async def extract_ssm_file(
    file: UploadFile = File(...), 
    token: str = Depends(get_api_key) # Protects this endpoint
):
    temp_path = f"temp_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = ocr.ocr(temp_path, cls=True)
        raw_lines = [res[1][0] for res in result[0]] if result and result[0] else []

        summary = parse_ssm_content(raw_lines)
        return {"success": True, "summary": summary}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)