"""
Helper Tools and Utilities
"""

from typing import Optional
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel

console = Console()


def format_error(error_type: str, message: str, traceback: str, code: Optional[str] = None) -> str:
    """
    Format error information for display
    
    Args:
        error_type: Type of error
        message: Error message
        traceback: Full traceback
        code: Original code (optional)
        
    Returns:
        Formatted error string
    """
    formatted = f"""
Error Type: {error_type}
Message: {message}

Traceback:
{traceback}
"""
    
    if code:
        formatted += f"\nOriginal Code:\n{code}"
    
    return formatted


def create_prompt(task: str, code: str, error: Optional[str] = None) -> str:
    """
    Create optimized prompt for Ollama (CPU-friendly, concise)
    
    Args:
        task: Task description (fix, analyze, create)
        code: Python code
        error: Error message (optional)
        
    Returns:
        Formatted prompt
    """
    if task == "fix":
        prompt = f"""Fix this Python code. The code has an error.

Code:
```python
{code}
```

Error:
{error}

Provide ONLY the corrected Python code without explanations. Start directly with the code."""
    
    elif task == "analyze":
        prompt = f"""Analyze this Python code and identify issues.

Code:
```python
{code}
```

List issues briefly:
1. 
2. 
3. """
    
    elif task == "create":
        prompt = f"""Create Python code for: {code}

Requirements:
- Complete, working code
- Include error handling
- Add brief comments

Provide ONLY the code."""
    
    elif task == "explain":
        prompt = f"""Explain this error briefly:

Error:
{error}

Code:
```python
{code}
```

Provide:
1. What caused it (1 line)
2. How to fix it (1 line)"""
    
    else:
        prompt = code
    
    return prompt


def extract_code(response: str) -> str:
    """
    Extract Python code from AI response
    
    Args:
        response: AI-generated response
        
    Returns:
        Extracted Python code
    """
    # Try to find code blocks
    if "```python" in response:
        start = response.find("```python") + 9
        end = response.find("```", start)
        if end != -1:
            return response[start:end].strip()
    
    if "```" in response:
        start = response.find("```") + 3
        end = response.find("```", start)
        if end != -1:
            return response[start:end].strip()
    
    # If no code blocks, return as is
    return response.strip()


def display_code(code: str, title: str = "Code"):
    """
    Display code with syntax highlighting
    
    Args:
        code: Python code to display
        title: Display title
    """
    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title=title, border_style="cyan"))


def display_diff(original: str, fixed: str):
    """
    Display difference between original and fixed code
    
    Args:
        original: Original code
        fixed: Fixed code
    """
    console.print("\n[yellow]═══ Original Code ═══[/yellow]")
    display_code(original, "Original")
    
    console.print("\n[green]═══ Fixed Code ═══[/green]")
    display_code(fixed, "Fixed")


def confirm_action(message: str) -> bool:
    """
    Ask user for confirmation
    
    Args:
        message: Confirmation message
        
    Returns:
        True if user confirms
    """
    response = input(f"{message} (y/n): ").strip().lower()
    return response in ['y', 'yes']


def truncate_text(text: str, max_length: int = 1000) -> str:
    """
    Truncate long text for display
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length] + "\n... (truncated)"


def format_traceback(traceback: str) -> str:
    """
    Format traceback for better readability
    
    Args:
        traceback: Raw traceback string
        
    Returns:
        Formatted traceback
    """
    lines = traceback.strip().split('\n')
    
    # Keep last 10 lines (most relevant)
    if len(lines) > 10:
        lines = lines[-10:]
    
    return '\n'.join(lines)