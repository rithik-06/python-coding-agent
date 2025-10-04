#!/usr/bin/env python3
"""
Python Debug Agent - Main Entry Point
A CPU-optimized AI agent for debugging and fixing Python code
"""

import argparse
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from src.agent import DebugAgent

console = Console()


def main():
    """Main entry point"""
    
    # ASCII Art Banner
    banner = """
    ╔═══════════════════════════════════════╗
    ║   🐍 Python Debug Agent 🤖           ║
    ║   AI-Powered Code Debugging          ║
    ║   Powered by Ollama (CPU Optimized)  ║
    ╚═══════════════════════════════════════╝
    """
    console.print(banner, style="cyan")
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="AI Agent for debugging Python code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --fix script.py          # Fix errors in a file
  python main.py --analyze script.py      # Analyze code quality
  python main.py --create "web scraper"   # Create new code
  python main.py --interactive            # Start interactive mode
  python main.py --code "print(x)"        # Debug inline code
        """
    )
    
    parser.add_argument(
        '--fix', '-f',
        metavar='FILE',
        help='Fix errors in a Python file'
    )
    
    parser.add_argument(
        '--analyze', '-a',
        metavar='FILE',
        help='Analyze a Python file for issues'
    )
    
    parser.add_argument(
        '--create', '-c',
        metavar='DESCRIPTION',
        help='Create new Python code from description'
    )
    
    parser.add_argument(
        '--code',
        metavar='CODE',
        help='Debug inline Python code'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Start interactive mode'
    )
    
    parser.add_argument(
        '--model', '-m',
        default='qwen2.5-coder:1.5b',
        help='Ollama model to use (default: qwen2.5-coder:1.5b)'
    )
    
    parser.add_argument(
        '--auto-apply',
        action='store_true',
        help='Automatically apply fixes without confirmation'
    )
    
    parser.add_argument(
        '--output', '-o',
        metavar='FILE',
        help='Output file for created code'
    )
    
    args = parser.parse_args()
    
    # Initialize agent
    try:
        agent = DebugAgent(model=args.model)
    except Exception as e:
        console.print(f"[red]Failed to initialize agent: {e}[/red]")
        console.print("[yellow]Make sure Ollama is running: ollama serve[/yellow]")
        return 1
    
    # Execute command
    try:
        if args.fix:
            # Fix a file
            if not Path(args.fix).exists():
                console.print(f"[red]File not found: {args.fix}[/red]")
                return 1
            
            success = agent.fix_file(args.fix, auto_apply=args.auto_apply)
            return 0 if success else 1
        
        elif args.analyze:
            # Analyze a file
            if not Path(args.analyze).exists():
                console.print(f"[red]File not found: {args.analyze}[/red]")
                return 1
            
            from src.file_handler import FileHandler
            file_handler = FileHandler()
            code = file_handler.read_file(args.analyze)
            
            if code:
                agent.analyze_code(code)
            return 0
        
        elif args.create:
            # Create new code
            code = agent.create_code(args.create, filepath=args.output)
            return 0 if code else 1
        
        elif args.code:
            # Debug inline code
            console.print("\n[cyan]🔍 Debugging inline code...[/cyan]\n")
            
            from src.code_executor import CodeExecutor
            executor = CodeExecutor()
            
            success, stdout, stderr = executor.execute_code(args.code)
            
            if success:
                console.print("[green]✓ Code runs successfully[/green]")
                if stdout:
                    console.print(f"\nOutput:\n{stdout}")
            else:
                console.print("[red]❌ Error detected[/red]")
                console.print(f"\n{stderr}")
                
                # Attempt to fix
                from src.tools import create_prompt, extract_code
                prompt = create_prompt("fix", args.code, stderr)
                fixed = agent.llm.generate(prompt, stream=False)
                
                if fixed:
                    fixed_code = extract_code(fixed)
                    console.print("\n[green]🔧 Suggested Fix:[/green]")
                    from src.tools import display_code
                    display_code(fixed_code, "Fixed Code")
            
            return 0
        
        elif args.interactive:
            # Interactive mode
            agent.interactive_mode()
            return 0
        
        else:
            # No arguments - show help and start interactive
            parser.print_help()
            console.print("\n[cyan]Starting interactive mode...[/cyan]\n")
            agent.interactive_mode()
            return 0
    
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Interrupted by user[/yellow]")
        return 130
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())