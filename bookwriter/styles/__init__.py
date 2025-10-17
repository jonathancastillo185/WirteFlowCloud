"""
Sistema de gestión de estilos de escritura para BookWriter AI.
Permite adaptar la generación de contenido según diferentes perfiles literarios.
"""

from .style_profiles import STYLE_PRESETS, WRITING_DIMENSIONS
from .style_manager import StyleManager
from .prompt_builder import PromptBuilder

__all__ = [
    'STYLE_PRESETS',
    'WRITING_DIMENSIONS', 
    'StyleManager',
    'PromptBuilder'
]