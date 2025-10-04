"""
Python AI Debugging Agent
A CPU-optimized agent for debugging and fixing Python code using Ollama.
"""

__version__ = "0.1.0"
__author__ = "Rithik Tiwari"

from .agent import DebugAgent
from .ollama_client import OllamaClient
from .file_handler import FileHandler
from .code_executor import CodeExecutor
from .tools import format_error, create_prompt

__all__ = [
    "DebugAgent",
    "OllamaClient", 
    "FileHandler",
    "CodeExecutor",
    "format_error",
    "create_prompt"
]