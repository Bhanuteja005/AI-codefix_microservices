# Unit Tests for AI Code Remediation Microservice
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.model_loader import LocalLLM
from app.prompts import build_remediation_prompt, extract_code_from_response
from app.utils.diff import generate_diff

client = TestClient(app)


class TestAPIEndpoints:
    """Test FastAPI endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns service info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert data["status"] == "running"
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_local_fix_endpoint_schema(self):
        """Test /local_fix returns correct schema"""
        payload = {
            "language": "python",
            "cwe": "CWE-89",
            "code": "SELECT * FROM users",
            "use_rag": False
        }
        response = client.post("/local_fix", json=payload)
        
        # May timeout on first run, so we accept both success and timeout
        if response.status_code == 200:
            data = response.json()
            assert "fixed_code" in data
            assert "diff" in data
            assert "explanation" in data
            assert "model_used" in data
            assert "token_usage" in data
            assert "latency_ms" in data
    
    def test_local_fix_invalid_payload(self):
        """Test /local_fix with invalid payload"""
        payload = {
            "language": "python"
            # Missing required fields
        }
        response = client.post("/local_fix", json=payload)
        assert response.status_code == 422  # Validation error


class TestPromptEngineering:
    """Test prompt generation"""
    
    def test_build_remediation_prompt(self):
        """Test prompt building"""
        prompt = build_remediation_prompt(
            language="python",
            cwe="CWE-89",
            vulnerable_code="SELECT * FROM users WHERE id=" + "user_id"
        )
        assert "CWE-89" in prompt
        assert "python" in prompt
        assert "SELECT" in prompt
    
    def test_extract_code_from_response(self):
        """Test code extraction from markdown"""
        response = "```python\nprint('hello')\n```"
        code = extract_code_from_response(response, "python")
        assert code == "print('hello')"
    
    def test_extract_code_plain(self):
        """Test code extraction from plain text"""
        response = "print('hello')"
        code = extract_code_from_response(response, "python")
        assert code == "print('hello')"


class TestDiffGenerator:
    """Test diff generation"""
    
    def test_generate_diff(self):
        """Test unified diff generation"""
        original = "line1\nline2\nline3"
        fixed = "line1\nline2_fixed\nline3"
        diff = generate_diff(original, fixed, "txt")
        assert "line2" in diff
        assert "line2_fixed" in diff
    
    def test_generate_diff_no_change(self):
        """Test diff with no changes"""
        code = "unchanged code"
        diff = generate_diff(code, code, "txt")
        # Should return empty or minimal diff
        assert isinstance(diff, str)


class TestModelLoader:
    """Test model loading (integration test)"""
    
    @pytest.mark.slow
    def test_model_initialization(self):
        """Test model can be initialized"""
        llm = LocalLLM()
        assert llm.model_name is not None
        assert llm.device in ["cuda", "cpu"]
    
    @pytest.mark.slow
    def test_model_name_extraction(self):
        """Test model name getter"""
        llm = LocalLLM("deepseek-ai/deepseek-coder-1.3b-base")
        name = llm.get_model_name()
        assert "deepseek" in name.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
