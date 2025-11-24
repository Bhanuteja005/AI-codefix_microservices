
# AI Code Remediation Microservice

**Local LLM + RAG-Enhanced Security Vulnerability Fixer**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

AI-powered microservice that automatically detects and fixes security vulnerabilities in source code using a local LLM (DeepSeek-Coder-1.3B) enhanced with RAG (Retrieval-Augmented Generation). Processes code through FastAPI endpoints, applies security fixes, and returns detailed reports with metrics.

**Core Capabilities:**
- Fixes 5 CWE types: SQL Injection (89), XSS (79), Hardcoded Secrets (798), SSRF (918), JWT Issues (347)
- Local inference - no cloud dependencies, full privacy
- RAG-enhanced with FAISS vector search over security guidelines
- Real-time metrics: token usage, latency, accuracy tracking

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
│                     (app/main.py)                            │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├─► POST /local_fix (Code Remediation)
                 │   Input: {vulnerable_code, cwe_id}
                 │   Output: {fixed_code, diff, explanation, metrics}
                 │
    ┌────────────┴───────────────────────────────────┐
    │                                                 │
┌───▼────────────────┐                   ┌───────────▼──────────┐
│   Local LLM        │                   │   RAG Retriever      │
│  (model_loader.py) │                   │  (rag/retriever.py)  │
│                    │                   │                      │
│ • DeepSeek-Coder   │◄──────────────────┤ • FAISS Index        │
│ • 1.3B params      │   Context Inject  │ • SentenceTransform  │
│ • 2.69 GB          │                   │ • 5 Recipes          │
└────────────────────┘                   └──────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────┐
│                  MetricsLogger (utils/logger.py)             │
│  • CSV logging (logs/metrics_YYYYMMDD_HHMMSS.csv)            │
│  • Token counting, latency tracking, accuracy measurement    │
└──────────────────────────────────────────────────────────────┘
```

**Data Flow:**
1. API receives vulnerable code + CWE ID
2. RAG retriever fetches relevant security guideline
3. Prompt builder creates remediation instruction
4. LLM generates fixed code
5. Response formatted with diff + metrics
6. Logs written to CSV file

## Project Structure

```
codefix/
├── app/
│   ├── main.py                # FastAPI app + /local_fix endpoint
│   ├── model_loader.py        # LLM loader (DeepSeek-Coder)
│   ├── prompts.py             # Prompt engineering
│   ├── rag/
│   │   ├── embedder.py        # SentenceTransformers
│   │   ├── retriever.py       # FAISS semantic search
│   │   └── recipes/           # 5 CWE guideline docs
│   └── utils/
│       ├── logger.py          # CSV metrics logging
│       └── diff.py            # Unified diff generation
├── test_local.py              # 3+ vulnerability test cases
├── requirements.txt           # Dependencies
├── Dockerfile                 # Container image
└── docker-compose.yml         # Orchestration
```

## Quick Start

### Installation

**Prerequisites:** Python 3.10+, 4GB RAM, AVX2 CPU

```powershell
# Clone repository
git clone <repo-url>
cd codefix

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Run Service

```powershell
# Start FastAPI server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Access Swagger UI
# Open browser: http://localhost:8000/docs
```

**First request takes 30-60s** (downloads 2.69GB model from HuggingFace). Subsequent requests: ~10-15s on CPU.

### Docker Deployment

```powershell
# Build and run
docker-compose up --build

# Access at http://localhost:8000
```

## API Usage

### POST /local_fix

**Request:**
```json
{
  "vulnerable_code": "query = 'SELECT * FROM users WHERE id=' + user_id",
  "cwe_id": "CWE-89"
}
```

**Response:**
```json
{
  "fixed_code": "query = 'SELECT * FROM users WHERE id=?' \ncursor.execute(query, (user_id,))",
  "diff": "- query = 'SELECT * FROM users WHERE id=' + user_id\n+ query = 'SELECT * FROM users WHERE id=?'\n+ cursor.execute(query, (user_id,))",
  "explanation": "Used parameterized query to prevent SQL injection",
  "model_used": "deepseek-ai/deepseek-coder-1.3b-base",
  "input_tokens": 245,
  "output_tokens": 78,
  "latency_ms": 12340
}
```

### Other Endpoints
- `GET /` - Service info
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

## Technical Details

### Local LLM
- **Model:** DeepSeek-Coder-1.3B (HuggingFace)
- **Size:** 2.69 GB
- **Framework:** PyTorch 2.9.1+cpu
- **Context Window:** 2048 tokens
- **Generation:** Temperature=0.2, max_new_tokens=512

### RAG System
- **Embedder:** all-MiniLM-L6-v2 (384 dimensions)
- **Vector Store:** FAISS with IndexFlatL2
- **Recipes:** 5 CWE guidelines (9,626 bytes total)
- **Retrieval:** Top-1 semantic match per query

### Logging
- **Format:** CSV with timestamp, CWE, tokens, latency
- **Location:** `logs/metrics_YYYYMMDD_HHMMSS.csv`
- **Tracked:** Input/output tokens, generation time, model name

## Compliance

✅ **Mandatory Requirements:**
- [x] Local open-source LLM (DeepSeek-Coder-1.3B)
- [x] FastAPI endpoint `/local_fix`
- [x] Input: vulnerable_code, cwe_id
- [x] Output: fixed_code, diff, explanation, model_used, tokens, latency
- [x] Logging system (CSV + console)
- [x] Testing suite (3+ test cases in test_local.py)
- [x] Documentation (README, API docs)

✅ **Optional Requirements:**
- [x] RAG component (FAISS + SentenceTransformers)
- [x] Docker support (Dockerfile + docker-compose.yml)
- [x] Unit tests (verify_implementation.py - 13 tests)

## Testing

```powershell
# Run integration tests (3 vulnerability types)
python test_local.py

# Verify all requirements
python verify_implementation.py

# Interactive testing via Swagger UI
# Navigate to http://localhost:8000/docs
```

## Troubleshooting

**Service won't start:**
- Check Python version: `python --version` (need 3.10+)
- Install missing packages: `pip install -r requirements.txt`
- Verify CPU has AVX2: FAISS requires it

**First request timeout:**
- Normal behavior (model download)
- Wait 30-60s for HuggingFace cache

**Slow inference (>20s):**
- Expected on CPU (10-15s typical)
- Use GPU for faster: Install `torch` with CUDA
- Reduce max_new_tokens in model_loader.py

**Protected namespace warning:**
- Harmless Pydantic warning
- Fixed with `model_config = {"protected_namespaces": ()}`

## Performance Optimization

**GPU Acceleration:**
```powershell
# Install CUDA-enabled PyTorch
pip install torch --index-url https://download.pytorch.org/whl/cu121

# Modify model_loader.py: device="cuda"
```

**Token Reduction:**
- Limit vulnerable_code to <500 lines
- Use specific CWE IDs (enables targeted RAG retrieval)
- Reduce max_new_tokens to 256 for simple fixes


