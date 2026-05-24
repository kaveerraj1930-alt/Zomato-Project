"""Groq LLM client with retries and timeout."""

import os
import time
from typing import Optional

try:
    from openai import OpenAI
except ImportError:
    raise ImportError(
        "OpenAI library is required. Install it with: pip install openai"
    )


class GroqClient:
    """Groq LLM client wrapper with retries and timeout."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "llama3-70b-8192",
        timeout: int = 30,
        max_retries: int = 3,
        base_url: str = "https://api.groq.com/openai/v1",
    ):
        """
        Initialize Groq client.
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            model: Model to use (default: llama3-70b-8192)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            base_url: Groq API base URL
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Groq API key not provided. Set GROQ_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=base_url,
            timeout=timeout,
        )

    def generate_completion(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Generate completion from Groq LLM with retries.
        
        Args:
            prompt: The prompt to send to the LLM
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            
        Returns:
            The generated completion text
            
        Raises:
            Exception: If all retry attempts fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content
                
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(
                        f"Failed to generate completion after {self.max_retries} attempts. "
                        f"Last error: {str(e)}"
                    )
        
        raise last_exception or Exception("Unknown error in generate_completion")

    def set_model(self, model: str) -> None:
        """Change the model being used."""
        self.model = model
