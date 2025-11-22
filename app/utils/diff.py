"""
Utility: Diff Generator
Creates unified diffs between original and fixed code
"""
import difflib
from typing import List


def generate_diff(original_code: str, fixed_code: str, language: str = "code") -> str:
    """
    Generate a unified diff between original and fixed code
    
    Args:
        original_code: The original vulnerable code
        fixed_code: The fixed secure code
        language: Programming language (for labeling)
        
    Returns:
        Unified diff string
    """
    original_lines = original_code.splitlines(keepends=True)
    fixed_lines = fixed_code.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        original_lines,
        fixed_lines,
        fromfile=f'original.{language}',
        tofile=f'fixed.{language}',
        lineterm=''
    )
    
    return ''.join(diff)


def generate_side_by_side_diff(original_code: str, fixed_code: str) -> str:
    """
    Generate a side-by-side diff representation
    
    Args:
        original_code: The original vulnerable code
        fixed_code: The fixed secure code
        
    Returns:
        Side-by-side diff string
    """
    original_lines = original_code.splitlines()
    fixed_lines = fixed_code.splitlines()
    
    diff_html = []
    diff_html.append("--- ORIGINAL | +++ FIXED")
    diff_html.append("-" * 50)
    
    max_lines = max(len(original_lines), len(fixed_lines))
    
    for i in range(max_lines):
        orig_line = original_lines[i] if i < len(original_lines) else ""
        fixed_line = fixed_lines[i] if i < len(fixed_lines) else ""
        
        if orig_line != fixed_line:
            if orig_line:
                diff_html.append(f"- {orig_line}")
            if fixed_line:
                diff_html.append(f"+ {fixed_line}")
        else:
            diff_html.append(f"  {orig_line}")
    
    return "\n".join(diff_html)
