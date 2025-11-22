"""
Prompt Engineering Templates
Contains structured prompts for code remediation
"""
from typing import Optional


def build_remediation_prompt(
    language: str,
    cwe: str,
    vulnerable_code: str,
    context: Optional[str] = None
) -> str:
    """
    Build a structured prompt for code remediation
    
    Args:
        language: Programming language (e.g., 'python', 'java')
        cwe: CWE identifier (e.g., 'CWE-89')
        vulnerable_code: The insecure code snippet
        context: Optional RAG-retrieved context/guidelines
        
    Returns:
        Formatted prompt string
    """
    
    base_prompt = f"""You are a security expert specialized in fixing vulnerable code.

**Task**: Fix the security vulnerability in the following {language} code.

**Vulnerability Type**: {cwe}

**Vulnerable Code**:
```{language}
{vulnerable_code}
```
"""
    
    if context:
        base_prompt += f"""
**Security Guidelines**:
{context}
"""
    
    base_prompt += """
**Instructions**:
1. Provide ONLY the fixed code without explanations
2. Maintain the original code structure and variable names
3. Fix the security vulnerability completely
4. Ensure the code is production-ready

**Fixed Code**:
```"""
    
    return base_prompt


def build_explanation_prompt(
    language: str,
    cwe: str,
    original_code: str,
    fixed_code: str
) -> str:
    """
    Build a prompt to generate an explanation of the fix
    
    Args:
        language: Programming language
        cwe: CWE identifier
        original_code: The original vulnerable code
        fixed_code: The fixed secure code
        
    Returns:
        Formatted prompt for explanation
    """
    
    prompt = f"""You are a security expert. Explain the security fix applied to the code.

**Original Vulnerable Code** ({language}, {cwe}):
```{language}
{original_code}
```

**Fixed Secure Code**:
```{language}
{fixed_code}
```

**Instructions**:
Provide a concise 2-3 sentence explanation of:
1. What vulnerability existed
2. How the fix addresses it
3. Why this approach is secure

**Explanation**:"""
    
    return prompt


def extract_code_from_response(response: str, language: str) -> str:
    """
    Extract code from LLM response
    
    Args:
        response: Raw LLM output
        language: Programming language for markdown detection
        
    Returns:
        Cleaned code snippet
    """
    # Remove markdown code blocks if present
    if f"```{language}" in response:
        parts = response.split(f"```{language}")
        if len(parts) > 1:
            code_part = parts[1].split("```")[0]
            return code_part.strip()
    elif "```" in response:
        parts = response.split("```")
        if len(parts) >= 3:
            return parts[1].strip()
    
    # Return as-is if no markdown blocks
    return response.strip()


def generate_cwe_context(cwe: str) -> str:
    """
    Generate contextual information about common CWEs
    
    Args:
        cwe: CWE identifier
        
    Returns:
        Brief context about the CWE
    """
    cwe_contexts = {
        "CWE-89": "SQL Injection - Use parameterized queries or prepared statements",
        "CWE-79": "Cross-Site Scripting (XSS) - Sanitize and escape user input",
        "CWE-78": "OS Command Injection - Avoid shell execution, use safe APIs",
        "CWE-798": "Hardcoded Credentials - Use environment variables or secret managers",
        "CWE-862": "Missing Authorization - Implement proper access control checks",
        "CWE-918": "SSRF - Validate and whitelist URLs before making requests",
        "CWE-502": "Deserialization - Validate input, use safe deserialization",
        "CWE-327": "Broken Crypto - Use strong, modern cryptographic algorithms",
        "CWE-22": "Path Traversal - Validate and sanitize file paths",
        "CWE-352": "CSRF - Implement anti-CSRF tokens"
    }
    
    return cwe_contexts.get(cwe, f"{cwe} - Apply security best practices")
