"""
FastAPI Main Application
AI Code Remediation Microservice
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Optional
import logging

from app.model_loader import get_llm_instance
from app.prompts import (
    build_remediation_prompt,
    extract_code_from_response,
    generate_cwe_context
)
from app.utils.diff import generate_diff
from app.utils.logger import get_logger_instance, Timer

# Optional RAG import
try:
    from app.rag.retriever import get_retriever_instance
    RAG_AVAILABLE = True
except Exception as e:
    logging.warning(f"RAG not available: {str(e)}")
    RAG_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Code Remediation Microservice",
    description="Local LLM-powered secure code generation with optional RAG",
    version="1.0.0"
)


# Request and Response Models
class CodeFixRequest(BaseModel):
    """Request model for code remediation"""
    language: str = Field(..., description="Programming language (e.g., 'python', 'java')")
    cwe: str = Field(..., description="CWE identifier (e.g., 'CWE-89')")
    code: str = Field(..., description="Vulnerable code snippet to fix")
    use_rag: bool = Field(default=True, description="Whether to use RAG for context retrieval")


class TokenUsage(BaseModel):
    """Token usage information"""
    input_tokens: int
    output_tokens: int


class CodeFixResponse(BaseModel):
    """Response model for code remediation"""
    model_config = {"protected_namespaces": ()}
    
    fixed_code: str = Field(..., description="The secure, fixed code")
    diff: str = Field(..., description="Unified diff between original and fixed code")
    explanation: str = Field(..., description="Explanation of the security fix")
    model_used: str = Field(..., description="Name of the LLM model used")
    token_usage: TokenUsage = Field(..., description="Token usage statistics")
    latency_ms: int = Field(..., description="Total processing latency in milliseconds")


# Initialize components on startup
@app.on_event("startup")
async def startup_event():
    """Initialize LLM and RAG components on startup"""
    logger.info("Starting AI Code Remediation Microservice...")
    
    try:
        # Load LLM
        logger.info("Loading local LLM...")
        llm = get_llm_instance()
        logger.info(f"LLM loaded: {llm.get_model_name()}")
        
        # Initialize RAG if available
        if RAG_AVAILABLE:
            logger.info("Initializing RAG component...")
            retriever = get_retriever_instance()
            if retriever.is_available():
                logger.info("RAG component ready")
            else:
                logger.warning("RAG component initialized but no recipes loaded")
        else:
            logger.info("RAG component not available")
        
        logger.info("Microservice ready to accept requests")
        
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "service": "AI Code Remediation Microservice",
        "status": "running",
        "version": "1.0.0",
        "rag_available": RAG_AVAILABLE
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/local_fix", response_model=CodeFixResponse)
async def local_fix(request: CodeFixRequest):
    """
    Main endpoint for code remediation
    
    Accepts vulnerable code and returns:
    - Fixed secure code
    - Diff between original and fixed
    - Explanation of the fix
    - Model information
    - Token usage
    - Latency metrics
    """
    logger.info(f"Received fix request - Language: {request.language}, CWE: {request.cwe}")
    
    # Start timing
    start_time = Timer()
    start_time.__enter__()
    
    try:
        # Get LLM instance
        llm = get_llm_instance()
        
        # Retrieve RAG context if enabled and available
        rag_context = None
        if request.use_rag and RAG_AVAILABLE:
            try:
                retriever = get_retriever_instance()
                if retriever.is_available():
                    # Create query from CWE and language
                    query = f"{request.cwe} {request.language} security vulnerability"
                    rag_context = retriever.retrieve(query)
                    logger.info("RAG context retrieved")
            except Exception as e:
                logger.warning(f"RAG retrieval failed: {str(e)}")
        
        # Build prompt
        if rag_context is None:
            # Fallback to built-in CWE context
            rag_context = generate_cwe_context(request.cwe)
        
        prompt = build_remediation_prompt(
            language=request.language,
            cwe=request.cwe,
            vulnerable_code=request.code,
            context=rag_context
        )
        
        # Generate fix
        logger.info("Generating code fix...")
        raw_output, token_usage = llm.generate_fix(prompt)
        
        # Extract fixed code
        fixed_code = extract_code_from_response(raw_output, request.language)
        
        # Handle case where model returns empty or unchanged code
        if not fixed_code or fixed_code == request.code:
            logger.warning("Model returned empty or unchanged code, using original")
            fixed_code = request.code
            explanation = f"The model could not generate a fix. Please review {request.cwe} guidelines manually."
        else:
            # Generate explanation (simplified - could be a separate LLM call)
            explanation = f"Fixed {request.cwe} vulnerability in {request.language} code. "
            if "parameter" in fixed_code.lower() or "%s" in fixed_code or "?" in fixed_code:
                explanation += "Applied parameterized queries to prevent injection. "
            if "environ" in fixed_code.lower() or "getenv" in fixed_code.lower():
                explanation += "Replaced hardcoded credentials with environment variables. "
            if "escape" in fixed_code.lower() or "textContent" in fixed_code.lower():
                explanation += "Applied proper output escaping to prevent XSS. "
            if not any(keyword in fixed_code.lower() for keyword in ["parameter", "environ", "escape"]):
                explanation += "Applied security best practices according to the CWE guidelines."
        
        # Generate diff
        diff = generate_diff(request.code, fixed_code, request.language)
        
        # Calculate latency before creating response
        start_time.__exit__(None, None, None)
        latency_ms = start_time.elapsed_ms
        
        # Prepare response
        response = CodeFixResponse(
            fixed_code=fixed_code,
            diff=diff if diff else "No changes detected",
            explanation=explanation,
            model_used=llm.get_model_name(),
            token_usage=TokenUsage(**token_usage),
            latency_ms=latency_ms
        )
        
        # Log metrics
        metrics_logger = get_logger_instance()
        metrics_logger.log_request({
            'language': request.language,
            'cwe': request.cwe,
            'input_tokens': token_usage['input_tokens'],
            'output_tokens': token_usage['output_tokens'],
            'latency_ms': latency_ms,
            'model_used': llm.get_model_name(),
            'rag_enabled': request.use_rag and rag_context is not None
        })
        
        logger.info(f"Request completed successfully in {latency_ms}ms")
        return response
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get summary statistics from the metrics log"""
    try:
        metrics_logger = get_logger_instance()
        stats = metrics_logger.get_summary_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to retrieve stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
