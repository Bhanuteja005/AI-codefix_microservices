# AI Code Remediation Microservice - Dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY test_local.py .

# Download the model (optional - can be done at runtime)
# Uncomment to pre-download model in Docker image
# RUN python -c "from transformers import AutoModelForCausalLM, AutoTokenizer; \
#     AutoModelForCausalLM.from_pretrained('deepseek-ai/deepseek-coder-1.3b-base'); \
#     AutoTokenizer.from_pretrained('deepseek-ai/deepseek-coder-1.3b-base')"

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_CACHE=/app/.cache

# Create cache directory
RUN mkdir -p /app/.cache

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
