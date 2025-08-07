"""
MOVA - Machine-Operable Verbal Actions
A declarative language for LLM interactions

MOVA - Machine-Operable Verbal Actions
Декларативна мова для взаємодії з LLM
"""

__version__ = "2.2.0"
__author__ = "Leryk1981"
__description__ = "Machine-Operable Verbal Actions - Declarative Language for LLM"

from .core import *
from .parser import *
from .validator import *

__all__ = [
    "__version__",
    "__author__", 
    "__description__"
] 