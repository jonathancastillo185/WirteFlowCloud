"""
Generador de páginas individuales para libros.
Maneja la escritura detallada de contenido página por página.
"""

from typing import Dict, Any, Callable, Tuple, Optional
from ..prompts.templates import PromptTemplates
from ..prompts.instructions import WritingInstructions
from ..styles.prompt_builder import PromptBuilder


class PageGenerator:
    """
    Generador especializado para escribir páginas individuales.
    Coordina contexto, estilo e instrucciones para generación coherente.
    """
    
    def __init__(self,
                 api_caller: Callable[[str], str],
                 prompt_builder: PromptBuilder):
        """
        Inicializa el generador de páginas.
        
        Args:
            api_caller: Función para llamar a la API de LLM
            prompt_builder: Constructor de prompts con estilo configurado
        """
        self.api_caller = api_caller
        self.prompt_builder = prompt_builder
    
    # ========================================================================
    # GENERACIÓN PRINCIPAL
    # ========================================================================
    
    def generate(self,
                chapter_info: Dict[str, Any],
                character_profiles: str,
                last_written_text: str,
                relevant_context: str,
                page_number: int,
                total_pages: int,
                scene_type: str = "mixed") -> Tuple[bool, str]:
        """
        Genera una página de contenido.
        
        Args:
            chapter_info: Información del capítulo actual
            character_profiles: Perfiles de personajes en escena
            last_written_text: Último fragmento escrito (para continuidad)
            relevant_context: Contexto de memoria semántica
            page_number: Número de página actual (1-indexed)
            total_pages: Total de páginas del capítulo
            scene_type: Tipo de escena ('action', 'dialogue', 'introspection', 'descriptive', 'mixed')
            
        Returns:
            Tupla (éxito: bool, contenido: str)
        """
        
        # Construir prompt completo
        prompt = self._build_full_prompt(
            chapter_info=chapter_info,
            character_profiles=character_profiles,
            last_written_text=last_written_text,
            relevant_context=relevant_context,
            page_number=page_number,
            total_pages=total_pages,
            scene_type=scene_type
        )
        
        # Llamar a la API
        content = self.api_caller(prompt)
        
        # Verificar que no haya error
        if "Error" in content or not content.strip():
            return False, content
        
        # Post-procesar el contenido
        content = self._post_process_content(content)
        
        return True, content
    
    # ========================================================================
    # CONSTRUCCIÓN DE PROMPT
    # ========================================================================
    
    def _build_full_prompt(self,
                          chapter_info: Dict[str, Any],
                          character_profiles: str,
                          last_written_text: str,
                          relevant_context: str,
                          page_number: int,
                          total_pages: int,
                          scene_type: str) -> str:
        """
        Construye el prompt completo para generar una página.
        
        Returns:
            Prompt completo listo para enviar a la API
        """
        
        # Usar el prompt builder del sistema de estilos
        base_prompt = self.prompt_builder.build_page_prompt(
            chapter_info=chapter_info,
            character_profiles=character_profiles,
            last_written_text=last_written_text,
            relevant_context=relevant_context,
            page_number=page_number,
            total_pages=total_pages
        )
        
        # Agregar instrucciones contextuales
        contextual_instructions = self._get_contextual_instructions(
            page_number=page_number,
            total_pages=total_pages,
            scene_type=scene_type
        )
        
        full_prompt = base_prompt + "\n" + contextual_instructions
        
        return full_prompt
    
    def _get_contextual_instructions(self,
                                    page_number: int,
                                    total_pages: int,
                                    scene_type: str) -> str:
        """
        Obtiene instrucciones contextuales según la posición y tipo de escena.
        
        Args:
            page_number: Número de página actual
            total_pages: Total de páginas
            scene_type: Tipo de escena
            
        Returns:
            Instrucciones contextuales combinadas
        """
        
        # Determinar posición en el capítulo
        if page_number == 1:
            position = "opening"
        elif page_number == total_pages:
            position = "closing"
        else:
            position = "middle"
        
        # Determinar ritmo según proximidad al final
        progress = page_number / total_pages
        if progress > 0.8:
            pace = "moderate"  # Aumentar tensión cerca del final
        else:
            pace = "moderate"
        
        # Obtener instrucciones combinadas
        instructions = WritingInstructions.get_contextual_instructions(
            page_position=position,
            scene_type=scene_type,
            pace=pace
        )
        
        return instructions
    
    # ========================================================================
    # POST-PROCESAMIENTO
    # ========================================================================
    
    def _post_process_content(self, content: str) -> str:
        """
        Post-procesa el contenido generado para limpieza y consistencia.
        
        Args:
            content: Contenido crudo generado
            
        Returns:
            Contenido procesado
        """
        
        # Limpiar posibles bloques de código markdown
        content = content.strip()
        content = content.replace("```markdown", "")
        content = content.replace("```", "")
        
        # Remover posibles títulos de capítulo si se colaron
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Saltar líneas que parecen títulos de capítulo
            if line.strip().startswith('##') or line.strip().startswith('# Capítulo'):
                continue
            cleaned_lines.append(line)
        
        content = '\n'.join(cleaned_lines).strip()
        
        # Asegurar que no haya espacios en blanco excesivos
        content = '\n\n'.join(paragraph.strip() for paragraph in content.split('\n\n') if paragraph.strip())
        
        return content
    
    # ========================================================================
    # UTILIDADES DE ANÁLISIS
    # ========================================================================
    
    def estimate_word_count(self, text: str) -> int:
        """
        Estima el conteo de palabras de un texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Número aproximado de palabras
        """
        return len(text.split())
    
    def analyze_content_quality(self, content: str) -> Dict[str, Any]:
        """
        Analiza métricas básicas de calidad del contenido.
        
        Args:
            content: Contenido a analizar
            
        Returns:
            Diccionario con métricas
        """
        
        words = content.split()
        sentences = content.split('.')
        paragraphs = [p for p in content.split('\n\n') if p.strip()]
        
        # Detectar diálogos (líneas con comillas)
        dialogue_lines = content.count('"') // 2
        
        return {
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "paragraph_count": len(paragraphs),
            "dialogue_lines": dialogue_lines,
            "avg_words_per_sentence": len(words) / max(len(sentences), 1),
            "has_dialogue": dialogue_lines > 0,
            "length_category": self._categorize_length(len(words))
        }
    
    def _categorize_length(self, word_count: int) -> str:
        """Categoriza la longitud del texto."""
        if word_count < 300:
            return "too_short"
        elif word_count < 400:
            return "short"
        elif word_count < 600:
            return "ideal"
        elif word_count < 700:
            return "long"
        else:
            return "too_long"
    
    # ========================================================================
    # DETECCIÓN DE TIPO DE ESCENA
    # ========================================================================
    
    def detect_scene_type(self, content: str) -> str:
        """
        Intenta detectar el tipo de escena predominante en el contenido.
        
        Args:
            content: Contenido a analizar
            
        Returns:
            Tipo de escena detectado
        """
        
        dialogue_ratio = content.count('"') / max(len(content), 1)
        action_verbs = ['corrió', 'saltó', 'golpeó', 'disparó', 'esquivó', 'atacó']
        action_count = sum(content.lower().count(verb) for verb in action_verbs)
        
        if dialogue_ratio > 0.15:
            return "dialogue"
        elif action_count > 5:
            return "action"
        elif len(content.split('\n\n')) <= 2 and len(content.split()) > 400:
            return "introspection"
        else:
            return "mixed"