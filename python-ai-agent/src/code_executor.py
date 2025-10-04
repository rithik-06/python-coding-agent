"""
Code Executor - Safely execute Python code and capture errors
"""

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Tuple
from rich.console import Console

console = Console()


class CodeExecutor:
    """Execute Python code safely in subprocess"""
    
    def __init__(self, timeout: int = 10):
        """
        Initialize code executor
        
        Args:
            timeout: Max execution time in seconds
        """
        self.timeout = timeout
    
    def execute_file(self, filepath: str) -> Tuple[bool, str, str]:
        """
        Execute a Python file
        
        Args:
            filepath: Path to Python file
            
        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            console.print(f"[cyan]Executing: {filepath}[/cyan]")
            
            result = subprocess.run(
                [sys.executable, filepath],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            success = result.returncode == 0
            stdout = result.stdout
            stderr = result.stderr
            
            if success:
                console.print("[green]✓ Execution successful[/green]")
                if stdout:
                    console.print("[dim]Output:[/dim]")
                    console.print(stdout)
            else:
                console.print("[red]✗ Execution failed[/red]")
                if stderr:
                    console.print("[red]Error:[/red]")
                    console.print(stderr)
            
            return success, stdout, stderr
            
        except subprocess.TimeoutExpired:
            error_msg = f"Execution timed out after {self.timeout} seconds"
            console.print(f"[red]{error_msg}[/red]")
            return False, "", error_msg
            
        except Exception as e:
            error_msg = f"Execution error: {str(e)}"
            console.print(f"[red]{error_msg}[/red]")
            return False, "", error_msg
    
    def execute_code(self, code: str) -> Tuple[bool, str, str]:
        """
        Execute Python code string
        
        Args:
            code: Python code to execute
            
        Returns:
            Tuple of (success, stdout, stderr)
        """
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False,
            encoding='utf-8'
        ) as tmp_file:
            tmp_file.write(code)
            tmp_path = tmp_file.name
        
        try:
            # Execute the temporary file
            success, stdout, stderr = self.execute_file(tmp_path)
            return success, stdout, stderr
            
        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)
    
    def validate_syntax(self, code: str) -> Tuple[bool, Optional[str]]:
        """
        Check if code has valid Python syntax
        
        Args:
            code: Python code to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            compile(code, '<string>', 'exec')
            return True, None
            
        except SyntaxError as e:
            error_msg = f"Syntax Error at line {e.lineno}: {e.msg}"
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            return False, error_msg
    
    def parse_error(self, stderr: str) -> dict:
        """
        Parse Python error from stderr
        
        Args:
            stderr: Error output
            
        Returns:
            Dictionary with error details
        """
        if not stderr:
            return {"type": "NoError", "message": "", "traceback": ""}
        
        lines = stderr.strip().split('\n')
        error_info = {
            "type": "Unknown",
            "message": "",
            "traceback": stderr,
            "line": None
        }
        
        # Find error type and message (usually last line)
        for line in reversed(lines):
            if ':' in line and any(err in line for err in [
                'Error', 'Exception', 'Warning'
            ]):
                parts = line.split(':', 1)
                error_info["type"] = parts[0].strip()
                error_info["message"] = parts[1].strip() if len(parts) > 1 else ""
                break
        
        # Find line number
        for line in lines:
            if 'line' in line.lower():
                try:
                    import re
                    match = re.search(r'line (\d+)', line)
                    if match:
                        error_info["line"] = int(match.group(1))
                except:
                    pass
        
        return error_info
    
    def quick_test(self, code: str) -> bool:
        """
        Quick syntax validation without execution
        
        Args:
            code: Python code to test
            
        Returns:
            True if syntax is valid
        """
        is_valid, _ = self.validate_syntax(code)
        return is_valid