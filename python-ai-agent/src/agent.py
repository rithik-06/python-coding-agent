"""
Debug Agent - Main orchestrator for debugging Python code
"""

from typing import Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .ollama_client import OllamaClient
from .file_handler import FileHandler
from .code_executor import CodeExecutor
from .tools import (
    create_prompt, 
    extract_code, 
    display_code, 
    display_diff,
    confirm_action,
    format_traceback
)

console = Console()


class DebugAgent:
    """AI Agent for debugging and fixing Python code"""
    
    def __init__(self, model: str = "qwen2.5-coder:1.5b", max_retries: int = 3):
        """
        Initialize debug agent
        
        Args:
            model: Ollama model to use
            max_retries: Maximum fix attempts
        """
        self.llm = OllamaClient(model=model)
        self.file_handler = FileHandler()
        self.executor = CodeExecutor()
        self.max_retries = max_retries
        
        # Check if model is available
        if not self.llm.check_model_available():
            console.print("[red]⚠ Model not available. Please pull it first.[/red]")
            console.print(f"[cyan]Run: ollama pull {model}[/cyan]")
    
    def fix_file(self, filepath: str, auto_apply: bool = False) -> bool:
        """
        Fix errors in a Python file
        
        Args:
            filepath: Path to the Python file
            auto_apply: Automatically apply fix without confirmation
            
        Returns:
            True if fixed successfully
        """
        console.print(f"\n[bold cyan]🔍 Analyzing file: {filepath}[/bold cyan]\n")
        
        # Read the file
        code = self.file_handler.read_file(filepath)
        if not code:
            return False
        
        # Execute and check for errors
        success, stdout, stderr = self.executor.execute_file(filepath)
        
        if success:
            console.print("[green]✓ No errors found! Code runs successfully.[/green]")
            return True
        
        # Parse error
        error_info = self.executor.parse_error(stderr)
        
        console.print(Panel(
            f"[red]Error Type:[/red] {error_info['type']}\n"
            f"[red]Message:[/red] {error_info['message']}\n"
            f"[red]Line:[/red] {error_info['line']}",
            title="❌ Error Detected",
            border_style="red"
        ))
        
        # Attempt to fix
        fixed_code = self._attempt_fix(code, format_traceback(stderr))
        
        if not fixed_code:
            console.print("[red]❌ Failed to generate fix[/red]")
            return False
        
        # Verify the fix
        console.print("\n[cyan]🧪 Testing fixed code...[/cyan]")
        is_valid, test_stdout, test_stderr = self.executor.execute_code(fixed_code)
        
        if not is_valid:
            console.print("[yellow]⚠ Fix didn't work, retrying...[/yellow]")
            
            # Retry with feedback
            for attempt in range(self.max_retries - 1):
                console.print(f"\n[cyan]Retry {attempt + 1}/{self.max_retries - 1}[/cyan]")
                fixed_code = self._attempt_fix(
                    fixed_code, 
                    f"Previous fix failed with: {test_stderr}"
                )
                
                is_valid, test_stdout, test_stderr = self.executor.execute_code(fixed_code)
                
                if is_valid:
                    break
        
        if not is_valid:
            console.print("[red]❌ Could not fix the error after multiple attempts[/red]")
            return False
        
        # Display the fix
        display_diff(code, fixed_code)
        
        # Apply fix
        if auto_apply or confirm_action("\n💾 Apply this fix to the file?"):
            if self.file_handler.write_file(filepath, fixed_code):
                console.print("[green]✓ File fixed successfully![/green]")
                return True
        else:
            console.print("[yellow]Fix not applied[/yellow]")
            return False
        
        return False
    
    def _attempt_fix(self, code: str, error: str) -> Optional[str]:
        """
        Attempt to fix code using AI
        
        Args:
            code: Original code
            error: Error message
            
        Returns:
            Fixed code or None
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[cyan]AI is analyzing and fixing..."),
            console=console
        ) as progress:
            progress.add_task("fix", total=None)
            
            # Create prompt
            prompt = create_prompt("fix", code, error)
            
            # Get fix from AI
            response = self.llm.generate(prompt, stream=False)
        
        if not response:
            return None
        
        # Extract code from response
        fixed_code = extract_code(response)
        return fixed_code
    
    def analyze_code(self, code: str) -> str:
        """
        Analyze code for potential issues
        
        Args:
            code: Python code to analyze
            
        Returns:
            Analysis report
        """
        console.print("\n[cyan]🔍 Analyzing code...[/cyan]\n")
        
        prompt = create_prompt("analyze", code)
        analysis = self.llm.generate(prompt, stream=True)
        
        return analysis
    
    def create_code(self, description: str, filepath: Optional[str] = None) -> Optional[str]:
        """
        Create new Python code from description
        
        Args:
            description: What the code should do
            filepath: Optional file path to save
            
        Returns:
            Generated code
        """
        console.print(f"\n[cyan]🤖 Creating code for: {description}[/cyan]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[cyan]Generating code..."),
            console=console
        ) as progress:
            progress.add_task("create", total=None)
            
            prompt = create_prompt("create", description)
            response = self.llm.generate(prompt, stream=False)
        
        if not response:
            console.print("[red]Failed to generate code[/red]")
            return None
        
        code = extract_code(response)
        display_code(code, "Generated Code")
        
        # Test the code
        console.print("\n[cyan]🧪 Testing generated code...[/cyan]")
        is_valid, stdout, stderr = self.executor.execute_code(code)
        
        if is_valid:
            console.print("[green]✓ Code works![/green]")
            
            if filepath:
                if self.file_handler.create_file(filepath, code):
                    console.print(f"[green]✓ Saved to: {filepath}[/green]")
        else:
            console.print("[yellow]⚠ Generated code has errors:[/yellow]")
            console.print(stderr)
        
        return code
    
    def explain_error(self, code: str, error: str) -> str:
        """
        Explain an error in simple terms
        
        Args:
            code: Code that caused error
            error: Error message
            
        Returns:
            Explanation
        """
        console.print("\n[cyan]📚 Explaining error...[/cyan]\n")
        
        prompt = create_prompt("explain", code, error)
        explanation = self.llm.generate(prompt, stream=True)
        
        return explanation
    
    def interactive_mode(self):
        """Start interactive debugging session"""
        console.print(Panel(
            "[bold cyan]🤖 Python Debug Agent[/bold cyan]\n"
            "Commands:\n"
            "  fix <file>     - Fix errors in a file\n"
            "  analyze <file> - Analyze code quality\n"
            "  create <desc>  - Create new code\n"
            "  help           - Show this help\n"
            "  exit           - Exit agent",
            title="Interactive Mode",
            border_style="cyan"
        ))
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    console.print("[cyan]👋 Goodbye![/cyan]")
                    break
                
                if user_input.lower() == 'help':
                    console.print(Panel(
                        "fix <file>     - Fix errors in a file\n"
                        "analyze <file> - Analyze code\n"
                        "create <desc>  - Create new code\n"
                        "exit           - Exit",
                        title="Help",
                        border_style="cyan"
                    ))
                    continue
                
                # Parse command
                parts = user_input.split(maxsplit=1)
                command = parts[