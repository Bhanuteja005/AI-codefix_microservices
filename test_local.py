"""
Test Script for AI Code Remediation Microservice
Tests the /local_fix endpoint with at least 3 vulnerabilities
"""
import requests
import json
import time
from typing import Dict, Any


# API endpoint
API_URL = "http://localhost:8000/local_fix"


def print_response(test_name: str, response_data: Dict[str, Any], elapsed_ms: int):
    """Pretty print the API response"""
    print(f"\n{'='*80}")
    print(f"TEST: {test_name}")
    print(f"{'='*80}")
    print(f"\n📊 Model Used: {response_data.get('model_used', 'N/A')}")
    print(f"⏱️  Latency: {response_data.get('latency_ms', 0)}ms (API reported)")
    print(f"⏱️  Total Time: {elapsed_ms}ms (including network)")
    print(f"\n🔢 Token Usage:")
    token_usage = response_data.get('token_usage', {})
    print(f"   - Input tokens:  {token_usage.get('input_tokens', 0)}")
    print(f"   - Output tokens: {token_usage.get('output_tokens', 0)}")
    print(f"   - Total tokens:  {token_usage.get('input_tokens', 0) + token_usage.get('output_tokens', 0)}")
    
    print(f"\n📝 Explanation:")
    print(f"   {response_data.get('explanation', 'N/A')}")
    
    print(f"\n🔧 Fixed Code:")
    print("-" * 80)
    print(response_data.get('fixed_code', 'N/A'))
    print("-" * 80)
    
    print(f"\n📋 Diff:")
    print("-" * 80)
    diff = response_data.get('diff', 'No diff available')
    if diff and diff != "No changes detected":
        print(diff)
    else:
        print("No changes detected or diff unavailable")
    print("-" * 80)


def test_sql_injection():
    """Test 1: SQL Injection vulnerability"""
    payload = {
        "language": "python",
        "cwe": "CWE-89",
        "code": "cursor.execute('SELECT * FROM users WHERE id=' + user_input)",
        "use_rag": True
    }
    
    print("\n🧪 Testing SQL Injection (CWE-89)...")
    start_time = time.time()
    
    try:
        response = requests.post(API_URL, json=payload, timeout=120)
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        if response.status_code == 200:
            print_response("SQL Injection (Python)", response.json(), elapsed_ms)
            return True
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_hardcoded_credentials():
    """Test 2: Hardcoded credentials vulnerability"""
    payload = {
        "language": "java",
        "cwe": "CWE-798",
        "code": '''String password = "MySecretPassword123!";
Connection conn = DriverManager.getConnection(dbURL, username, password);''',
        "use_rag": True
    }
    
    print("\n🧪 Testing Hardcoded Credentials (CWE-798)...")
    start_time = time.time()
    
    try:
        response = requests.post(API_URL, json=payload, timeout=120)
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        if response.status_code == 200:
            print_response("Hardcoded Credentials (Java)", response.json(), elapsed_ms)
            return True
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_xss_vulnerability():
    """Test 3: Cross-Site Scripting (XSS) vulnerability"""
    payload = {
        "language": "javascript",
        "cwe": "CWE-79",
        "code": '''let userInput = req.query.name;
document.getElementById('greeting').innerHTML = "Hello " + userInput;''',
        "use_rag": True
    }
    
    print("\n🧪 Testing Cross-Site Scripting (CWE-79)...")
    start_time = time.time()
    
    try:
        response = requests.post(API_URL, json=payload, timeout=120)
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        if response.status_code == 200:
            print_response("Cross-Site Scripting (JavaScript)", response.json(), elapsed_ms)
            return True
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_health_check():
    """Test the health endpoint"""
    print("\n🏥 Testing Health Check Endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ Health check passed: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False


def test_root_endpoint():
    """Test the root endpoint"""
    print("\n🏠 Testing Root Endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Service: {data.get('service', 'N/A')}")
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Version: {data.get('version', 'N/A')}")
            print(f"   RAG Available: {data.get('rag_available', False)}")
            return True
        else:
            print(f"❌ Root endpoint failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("="*80)
    print("AI CODE REMEDIATION MICROSERVICE - TEST SUITE")
    print("="*80)
    print("\nThis script tests the /local_fix endpoint with multiple vulnerabilities.")
    print("Make sure the FastAPI service is running on http://localhost:8000")
    print("\nStarting tests in 3 seconds...")
    time.sleep(3)
    
    results = []
    
    # Health checks
    results.append(("Health Check", test_health_check()))
    results.append(("Root Endpoint", test_root_endpoint()))
    
    # Main vulnerability tests
    results.append(("SQL Injection", test_sql_injection()))
    results.append(("Hardcoded Credentials", test_hardcoded_credentials()))
    results.append(("XSS Vulnerability", test_xss_vulnerability()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:30s} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed successfully!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
