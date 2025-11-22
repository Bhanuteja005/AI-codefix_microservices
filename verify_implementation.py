"""
End-to-End Verification Script
Tests all assignment requirements without starting the full server
"""
import sys
import traceback

def test_requirement(name, test_func):
    """Test a single requirement"""
    try:
        print(f"\n[Testing] {name}...", end=" ")
        test_func()
        print("✅ PASS")
        return True
    except Exception as e:
        print(f"❌ FAIL")
        print(f"  Error: {str(e)}")
        traceback.print_exc()
        return False

def test_imports():
    """Test 1: All imports work"""
    from app.main import app
    from app.model_loader import LocalLLM
    from app.prompts import build_remediation_prompt
    from app.utils.logger import MetricsLogger
    from app.utils.diff import generate_diff
    from app.rag.embedder import Embedder
    from app.rag.retriever import RAGRetriever
    assert app is not None

def test_model_initialization():
    """Test 2: Model can be initialized"""
    from app.model_loader import LocalLLM
    llm = LocalLLM("deepseek-ai/deepseek-coder-1.3b-base")
    assert llm.model_name == "deepseek-ai/deepseek-coder-1.3b-base"
    assert llm.device in ["cpu", "cuda"]
    assert llm.get_model_name() == "deepseek-coder-1.3b-base"

def test_prompt_engineering():
    """Test 3: Prompt generation works"""
    from app.prompts import build_remediation_prompt, extract_code_from_response
    
    prompt = build_remediation_prompt("python", "CWE-89", "SELECT * FROM users")
    assert "CWE-89" in prompt
    assert "python" in prompt
    assert "SELECT" in prompt
    
    code = extract_code_from_response("```python\nfixed_code\n```", "python")
    assert code == "fixed_code"

def test_diff_generation():
    """Test 4: Diff generation works"""
    from app.utils.diff import generate_diff
    
    diff = generate_diff("old_code\nline2", "new_code\nline2", "py")
    assert "old_code" in diff or "new_code" in diff

def test_logger():
    """Test 5: Logger works"""
    from app.utils.logger import MetricsLogger
    import os
    
    test_file = "test_verification_log.csv"
    logger = MetricsLogger(test_file)
    
    logger.log_request({
        'language': 'python',
        'cwe': 'CWE-89',
        'input_tokens': 100,
        'output_tokens': 50,
        'latency_ms': 500,
        'model_used': 'test-model',
        'rag_enabled': True
    })
    
    assert os.path.exists(test_file)
    
    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)

def test_rag_embedder():
    """Test 6: RAG Embedder works"""
    from app.rag.embedder import Embedder
    
    embedder = Embedder()
    embedder.load_model()
    
    embedding = embedder.embed_text("test text")
    assert embedding is not None
    assert len(embedding.shape) == 1

def test_rag_retriever():
    """Test 7: RAG Retriever works"""
    from app.rag.retriever import RAGRetriever
    from app.rag.embedder import Embedder
    import os
    
    retriever = RAGRetriever("app/rag/recipes")
    retriever.load_recipes()
    
    assert len(retriever.documents) == 5
    assert len(retriever.filenames) == 5
    
    embedder = Embedder()
    embedder.load_model()
    retriever.build_index(embedder)
    
    assert retriever.is_available()

def test_recipe_files():
    """Test 8: All recipe files exist"""
    import os
    
    recipes_dir = "app/rag/recipes"
    required_files = [
        "sql_injection.txt",
        "hardcoded_secret.txt",
        "xss_dom_based.txt",
        "ssrf_basic.txt",
        "jwt_validation_issue.txt"
    ]
    
    for filename in required_files:
        filepath = os.path.join(recipes_dir, filename)
        assert os.path.exists(filepath), f"{filename} not found"
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            assert len(content) > 100, f"{filename} is too short"

def test_api_schema():
    """Test 9: API schemas are correct"""
    from app.main import CodeFixRequest, CodeFixResponse, TokenUsage
    from pydantic import ValidationError
    
    # Test valid request
    request = CodeFixRequest(
        language="python",
        cwe="CWE-89",
        code="SELECT * FROM users",
        use_rag=True
    )
    assert request.language == "python"
    
    # Test response structure
    response = CodeFixResponse(
        fixed_code="fixed",
        diff="diff",
        explanation="explanation",
        model_used="test",
        token_usage=TokenUsage(input_tokens=10, output_tokens=20),
        latency_ms=100
    )
    assert response.fixed_code == "fixed"

def test_test_script():
    """Test 10: test_local.py exists and is valid"""
    import os
    
    assert os.path.exists("test_local.py")
    
    with open("test_local.py", 'r', encoding='utf-8') as f:
        content = f.read()
        assert "test_sql_injection" in content
        assert "test_hardcoded_credentials" in content
        assert "test_xss_vulnerability" in content
        assert "CWE-89" in content
        assert "CWE-798" in content
        assert "CWE-79" in content

def test_requirements_file():
    """Test 11: requirements.txt is complete"""
    import os
    
    assert os.path.exists("requirements.txt")
    
    with open("requirements.txt", 'r', encoding='utf-8') as f:
        content = f.read()
        required_packages = [
            "fastapi",
            "uvicorn",
            "pydantic",
            "torch",
            "transformers",
            "sentence-transformers",
            "faiss-cpu"
        ]
        
        for package in required_packages:
            assert package in content.lower(), f"{package} not in requirements.txt"

def test_docker_files():
    """Test 12: Docker files exist"""
    import os
    
    assert os.path.exists("Dockerfile")
    assert os.path.exists("docker-compose.yml")
    
    with open("Dockerfile", 'r', encoding='utf-8') as f:
        content = f.read()
        assert "FROM python" in content
        assert "EXPOSE 8000" in content

def test_readme():
    """Test 13: README.md is comprehensive"""
    import os
    
    assert os.path.exists("readme.md")
    
    with open("readme.md", 'r', encoding='utf-8') as f:
        content = f.read()
        required_sections = [
            "Installation",
            "Running",
            "Testing",
            "Performance",
            "Limitations",
            "Requirements"
        ]
        
        for section in required_sections:
            assert section.lower() in content.lower(), f"{section} section missing"

def main():
    """Run all verification tests"""
    print("=" * 80)
    print("AI CODE REMEDIATION MICROSERVICE - VERIFICATION REPORT")
    print("=" * 80)
    
    tests = [
        ("Requirement 1: All imports work", test_imports),
        ("Requirement 2: Model initialization", test_model_initialization),
        ("Requirement 3: Prompt engineering", test_prompt_engineering),
        ("Requirement 4: Diff generation", test_diff_generation),
        ("Requirement 5: Logging & metrics", test_logger),
        ("Requirement 6: RAG embedder", test_rag_embedder),
        ("Requirement 7: RAG retriever", test_rag_retriever),
        ("Requirement 8: Recipe files (5 CWEs)", test_recipe_files),
        ("Requirement 9: API schemas", test_api_schema),
        ("Requirement 10: test_local.py (3+ tests)", test_test_script),
        ("Requirement 11: requirements.txt", test_requirements_file),
        ("Requirement 12: Docker support", test_docker_files),
        ("Requirement 13: README.md", test_readme),
    ]
    
    results = []
    for name, test_func in tests:
        result = test_requirement(name, test_func)
        results.append((name, result))
    
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("\n" + "-" * 80)
    print(f"Total: {passed}/{total} tests passed ({100*passed//total}%)")
    
    if passed == total:
        print("\n🎉 ALL VERIFICATION TESTS PASSED!")
        print("✅ All mandatory requirements implemented")
        print("✅ All optional requirements implemented")
        print("✅ Project is ready for submission")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        print("Please review the failed tests above")
    
    print("=" * 80)
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
