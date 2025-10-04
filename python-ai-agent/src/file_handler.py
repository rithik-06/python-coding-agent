"""
File Handler - Read and write Python files
"""

import os
from pathlib import Path
from typing import Optional
from rich.console import Console

console = Console()


class FileHandler:
    """Handle file operations for Python files"""
    
    def __init__(self, base_dir: str = "."):
        """
        Initialize file handler
        
        Args:
            base_dir: Base directory for file operations
        """
        self.base_dir = Path(base_dir)
    
    def read_file(self, filepath: str) -> Optional[str]:
        """
        Read content from a Python file
        
        Args:
            filepath: Path to the file
            
        Returns:
            File content as string, or None if error
        """
        try:
            file_path = self.base_dir / filepath
            
            if not file_path.exists():
                console.print(f"[red]File not found: {filepath}[/red]")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            console.print(f"[green]✓ Read file: {filepath}[/green]")
            return content
            
        except Exception as e:
            console.print(f"[red]Error reading file {filepath}: {e}[/red]")
            return None
    
    def write_file(self, filepath: str, content: str, backup: bool = True) -> bool:
        """
        Write content to a Python file
        
        Args:
            filepath: Path to the file
            content: Content to write
            backup: Create backup before writing
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self.base_dir / filepath
            
            # Create backup if file exists
            if backup and file_path.exists():
                backup_path = file_path.with_suffix('.py.bak')
                file_path.rename(backup_path)
                console.print(f"[yellow]Created backup: {backup_path.name}[/yellow]")
            
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            console.print(f"[green]✓ Wrote file: {filepath}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]Error writing file {filepath}: {e}[/red]")
            return False
    
    def list_python_files(self, directory: str = ".") -> list[str]:
        """
        List all Python files in a directory
        
        Args:
            directory: Directory to search
            
        Returns:
            List of Python file paths
        """
        try:
            dir_path = self.base_dir / directory
            python_files = list(dir_path.rglob("*.py"))
            
            # Filter out __pycache__ and venv
            python_files = [
                str(f.relative_to(self.base_dir)) 
                for f in python_files 
                if '__pycache__' not in str(f) and '.venv' not in str(f)
            ]
            
            return python_files
            
        except Exception as e:
            console.print(f"[red]Error listing files: {e}[/red]")
            return []
    
    def create_file(self, filepath: str, content: str) -> bool:
        """
        Create a new Python file
        
        Args:
            filepath: Path for the new file
            content: Initial content
            
        Returns:
            True if successful, False otherwise
        """
        file_path = self.base_dir / filepath
        
        if file_path.exists():
            console.print(f"[yellow]File already exists: {filepath}[/yellow]")
            response = input("Overwrite? (y/n): ")
            if response.lower() != 'y':
                return False
        
        return self.write_file(filepath, content, backup=False)
    
    def get_file_info(self, filepath: str) -> dict:
        """
        Get information about a file
        
        Args:
            filepath: Path to the file
            
        Returns:
            Dictionary with file info
        """
        try:
            file_path = self.base_dir / filepath
            
            if not file_path.exists():
                return {"exists": False}
            
            stat = file_path.stat()
            content = self.read_file(filepath)
            
            return {
                "exists": True,
                "size": stat.st_size,
                "lines": len(content.splitlines()) if content else 0,
                "modified": stat.st_mtime,
            }
            
        except Exception as e:
            console.print(f"[red]Error getting file info: {e}[/red]")
            return {"exists": False, "error": str(e)}