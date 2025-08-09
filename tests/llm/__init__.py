"""
LLM tests
Тести для LLM
"""

# Import LLM test modules
from .test_llm_client import TestLLMClient
from .test_openrouter import TestOpenRouter

__all__ = [
    "TestLLMClient",
    "TestOpenRouter"
]