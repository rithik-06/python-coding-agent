"""
Ollama Client - Optimized for CPU
Handles communication with local Ollama models
"""

import ollama
from typing import Generator
from rich.console import Console

console = Console()


class OllamaClient:
    """Client for interacting with Ollama models"""
    
    def __init__(self, model: str = "qwen2.5-coder:1.5b"):
        """
        Initialize Ollama client
        
        Args:
            model: Model name (default: qwen2.5-coder:1.5b for CPU)
        """
        self.model = model
        self.client = ollama.Client()
        
    def generate(self, prompt: str, stream: bool = True) -> str:
        """
        Generate response from Ollama
        
        Args:
            prompt: Input prompt
            stream: Whether to stream response
            
        Returns:
            Generated text response
        """
        try:
            if stream:
                return self._generate_stream(prompt)
            else:
                response = self.client.generate(
                    model=self.model,
                    prompt=prompt,
                    options={
                        "temperature": 0.3,  # Lower for more deterministic code
                        "top_p": 0.9,
                        "num_predict": 2048,  # Max tokens
                    }
                )
                return response['response']
                
        except Exception as e:
            console.print(f"[red]Error generating response: {e}[/red]")
            return ""
    
    def _generate_stream(self, prompt: str) -> str:
        """Stream response from Ollama"""
        full_response = ""
        
        try:
            stream = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=True,
                options={
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 2048,
                }
            )
            
            console.print("[cyan]AI Response:[/cyan]", end=" ")
            
            for chunk in stream:
                token = chunk['response']
                full_response += token
                console.print(token, end="")
            
            console.print()  # New line after streaming
            return full_response
            
        except Exception as e:
            console.print(f"\n[red]Streaming error: {e}[/red]")
            return full_response
    
    def check_model_available(self) -> bool:
        """Check if the model is available locally"""
        try:
            models = self.client.list()
            available_models = [m['name'] for m in models.get('models', [])]
            
            if self.model in available_models:
                return True
            else:
                console.print(f"[yellow]Model '{self.model}' not found![/yellow]")
                console.print(f"[yellow]Available models: {', '.join(available_models)}[/yellow]")
                console.print(f"[cyan]Pull it with: ollama pull {self.model}[/cyan]")
                return False
                
        except Exception as e:
            console.print(f"[red]Error checking models: {e}[/red]")
            console.print("[yellow]Make sure Ollama is running: ollama serve[/yellow]")
            return False