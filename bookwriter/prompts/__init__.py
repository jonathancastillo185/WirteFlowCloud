"""
Sistema de templates de prompts reutilizables.
Separa la lógica de construcción de prompts del código de negocio.
"""

from .templates import PromptTemplates
from .instructions import WritingInstructions

__all__ = [
    'PromptTemplates',
    'WritingInstructions'
]