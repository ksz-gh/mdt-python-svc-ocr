FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 libgomp1 libsm6 libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# 1. Install standard requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html

# 2. Copy the entire libs folder
COPY libs/ /tmp/libs/

# 3. USE A WILDCARD to install any .whl file found in that folder
# This handles version bumps (1.0 -> 1.1) automatically
RUN pip install /tmp/libs/*.whl && rm -rf /tmp/libs/

# 4. Copy application code
COPY main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]