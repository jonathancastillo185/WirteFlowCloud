"""
Constructor dinámico de prompts adaptados al estilo de escritura configurado.
Genera instrucciones específicas para el modelo según el perfil activo.
"""

from typing import Dict, List, Any
from .style_profiles import WRITING_DIMENSIONS, get_dimension_info


class PromptBuilder:
    """
    Construye prompts dinámicos para la generación de contenido
    adaptados al perfil de estilo configurado.
    """
    
    def __init__(self, style_config: Dict[str, Any]):
        """
        Inicializa el constructor de prompts.
        
        Args:
            style_config: Configuración completa del estilo desde StyleManager
        """
        self.style_config = style_config
        self.dimensions = style_config.get('dimensions', {})
        self.special_instructions = style_config.get('special_instructions', [])
        self.avoid_list = style_config.get('avoid', [])
        self.examples = style_config.get('examples', [])
    
    # ========================================================================
    # PROMPT DEL SISTEMA (Base)
    # ========================================================================
    
    def build_system_prompt(self, book_metadata: Dict[str, Any]) -> str:
        """
        Construye el prompt del sistema base para mantener consistencia.
        
        Args:
            book_metadata: Información del libro (título, autor, premisa, temas)
            
        Returns:
            Prompt del sistema completo
        """
        author_style = book_metadata.get('author_style', 'neutral')
        title = book_metadata.get('title', 'Sin Título')
        premise = book_metadata.get('premise', 'No especificada')
        themes = book_metadata.get('themes', [])
        
        prompt = f"""Eres un escritor experto en el estilo de {author_style}.

**INFORMACIÓN DE LA NOVELA:**
- **Título:** {title}
- **Premisa:** {premise}
- **Temas:** {', '.join(themes) if themes else 'A desarrollar'}

"""
        
        # Agregar perfil de estilo
        prompt += self._build_style_section()
        
        # Agregar instrucciones especiales
        if self.special_instructions:
            prompt += self._build_special_instructions_section()
        
        # Agregar qué evitar
        if self.avoid_list:
            prompt += self._build_avoid_section()
        
        return prompt
    
    # ========================================================================
    # PROMPT PARA GENERACIÓN DE OUTLINE
    # ========================================================================
    
    def build_outline_prompt(self, 
                            premise: str, 
                            num_chapters: int, 
                            themes: str,
                            author_style: str) -> str:
        """
        Construye el prompt para generación de outline adaptado al estilo.
        
        Args:
            premise: Premisa de la historia
            num_chapters: Número de capítulos
            themes: Temas a explorar
            author_style: Estilo del autor
            
        Returns:
            Prompt completo para outline
        """
        
        # Obtener características del estilo narrativo
        narrative_density = self.dimensions.get('narrative_density', 'balanced')
        thematic_depth = self.dimensions.get('thematic_depth', 'layered')
        
        narrative_info = get_dimension_info('narrative_density', narrative_density)
        thematic_info = get_dimension_info('thematic_depth', thematic_depth)
        
        prompt = f"""Basado en la siguiente premisa, temas y estilo, genera un outline detallado para una novela de {num_chapters} capítulos.

**PREMISA:** {premise}
**TEMAS:** {themes}
**ESTILO:** {author_style}

**PERFIL NARRATIVO:**
- **Densidad Narrativa:** {narrative_info.get('name', 'Equilibrado')}
  {narrative_info.get('description', '')}
  
- **Profundidad Temática:** {thematic_info.get('name', 'Por Capas')}
  {thematic_info.get('description', '')}

"""
        
        # Instrucciones específicas según el tipo narrativo
        prompt += self._build_outline_instructions(narrative_density, thematic_depth)
        
        # Estructura JSON requerida
        prompt += """

**ESTRUCTURA JSON REQUERIDA:**
```json
{
    "world": {
        "setting": "Descripción del escenario principal",
        "time_period": "Período temporal",
        "key_locations": {
            "Lugar 1": "Descripción",
            "Lugar 2": "Descripción"
        },
        "rules_of_the_world": ["Regla 1", "Regla 2"]
    },
    "characters": {
        "Nombre Personaje": {
            "description": "Descripción física y de fondo",
            "personality": "Rasgos de personalidad clave",
            "story_arc": "Evolución a lo largo de la historia",
            "relationships": "Conexiones con otros personajes",
            "internal_conflict": "Conflicto interno principal"
        }
    },
    "style": {
        "tone": "Tono general de la narrativa",
        "point_of_view": "Primera persona / Tercera persona limitada / Omnisciente",
        "tense": "Presente / Pasado"
    },
    "plot": {
        "outline": [
            {
                "number": 1,
                "title": "Título del capítulo",
                "summary": "Resumen de eventos principales",
                "key_events": ["Evento 1", "Evento 2", "Evento 3"],
                "character_focus": ["Personaje 1", "Personaje 2"],
                "emotional_arc": "Progresión emocional del capítulo",
                "pages_estimate": 10
            }
        ]
    },
    "consistency_rules": [
        "Regla de consistencia 1",
        "Regla de consistencia 2"
    ]
}
```

**IMPORTANTE:** Tu respuesta debe ser ÚNICAMENTE el JSON válido, sin texto adicional antes o después.
"""
        
        return prompt
    
    # ========================================================================
    # PROMPT PARA GENERACIÓN DE PÁGINA
    # ========================================================================
    
    def build_page_prompt(self,
                         chapter_info: Dict[str, Any],
                         character_profiles: str,
                         last_written_text: str,
                         relevant_context: str,
                         page_number: int,
                         total_pages: int) -> str:
        """
        Construye el prompt para generar una página específica.
        
        Args:
            chapter_info: Información del capítulo actual
            character_profiles: Perfiles de personajes relevantes
            last_written_text: Último fragmento escrito
            relevant_context: Contexto de memoria semántica
            page_number: Número de página actual
            total_pages: Total de páginas del capítulo
            
        Returns:
            Prompt completo para generación de página
        """
        
        prompt = f"""Estás escribiendo la página {page_number} de {total_pages} del siguiente capítulo:

**CAPÍTULO {chapter_info.get('number', 'N/A')}: "{chapter_info.get('title', 'Sin Título')}"**

**EVENTOS QUE DEBEN OCURRIR EN ESTE CAPÍTULO:**
{chapter_info.get('summary', 'No especificado')}

**EVENTOS CLAVE:**
{self._format_key_events(chapter_info.get('key_events', []))}

**PERSONAJES EN ESCENA:**
{character_profiles if character_profiles else "No hay personajes específicos en foco"}

"""
        
        # Agregar contexto previo si existe
        if relevant_context and relevant_context != "No hay contexto disponible en la memoria a largo plazo.":
            prompt += f"""**CONTEXTO RELEVANTE DE CAPÍTULOS ANTERIORES:**
{relevant_context}

"""
        
        # Agregar último texto escrito
        if last_written_text:
            prompt += f"""**ÚLTIMO FRAGMENTO ESCRITO (Continúa DIRECTAMENTE desde aquí):**
...{last_written_text}

"""
        else:
            prompt += "**[INICIO DEL CAPÍTULO]**\n\n"
        
        # Agregar instrucciones de estilo específicas
        prompt += self._build_page_writing_instructions(page_number, total_pages)
        
        # Longitud objetivo
        prompt += self._build_length_instruction(page_number, total_pages)
        
        return prompt
    
    # ========================================================================
    # SECCIONES DEL PROMPT
    # ========================================================================
    
    def _build_style_section(self) -> str:
        """Construye la sección de descripción del estilo."""
        
        section = "**PERFIL DE ESTILO CONFIGURADO:**\n\n"
        
        # Recorrer cada dimensión configurada
        for dimension_key, level in self.dimensions.items():
            if dimension_key in WRITING_DIMENSIONS:
                dimension_data = WRITING_DIMENSIONS[dimension_key]
                if level in dimension_data:
                    level_data = dimension_data[level]
                    section += f"- **{dimension_key.replace('_', ' ').title()}:** {level_data['name']}\n"
                    section += f"  {level_data['description']}\n"
                    
                    # Agregar características clave
                    if 'characteristics' in level_data:
                        section += "  Características:\n"
                        for char in level_data['characteristics'][:3]:  # Limitar a 3
                            section += f"    • {char}\n"
                    section += "\n"
        
        return section
    
    def _build_special_instructions_section(self) -> str:
        """Construye la sección de instrucciones especiales."""
        
        section = "**INSTRUCCIONES ESPECIALES PARA ESTE ESTILO:**\n\n"
        
        for i, instruction in enumerate(self.special_instructions, 1):
            section += f"{i}. {instruction}\n"
        
        section += "\n"
        return section
    
    def _build_avoid_section(self) -> str:
        """Construye la sección de elementos a evitar."""
        
        section = "**EVITA LO SIGUIENTE:**\n\n"
        
        for item in self.avoid_list:
            section += f"- ❌ {item}\n"
        
        section += "\n"
        return section
    
    def _build_outline_instructions(self, narrative_density: str, thematic_depth: str) -> str:
        """Construye instrucciones específicas para outline según estilo."""
        
        instructions = "**INSTRUCCIONES PARA EL OUTLINE:**\n\n"
        
        # Instrucciones según densidad narrativa
        if narrative_density == "fast_paced":
            instructions += "- Cada capítulo debe tener múltiples eventos significativos\n"
            instructions += "- Capítulos cortos (8-12 páginas estimadas)\n"
            instructions += "- Cliffhangers y giros frecuentes\n"
        elif narrative_density == "contemplative":
            instructions += "- Permite capítulos enfocados en desarrollo interno\n"
            instructions += "- Capítulos más largos (15-20 páginas estimadas)\n"
            instructions += "- Espacio para reflexión y atmósfera\n"
        elif narrative_density == "epic":
            instructions += "- Múltiples líneas argumentales pueden entrelazarse\n"
            instructions += "- Capítulos extensos (18-25 páginas estimadas)\n"
            instructions += "- Worldbuilding detallado integrado en la trama\n"
        else:  # balanced
            instructions += "- Balance entre acción y desarrollo\n"
            instructions += "- Capítulos de longitud estándar (12-15 páginas estimadas)\n"
            instructions += "- Variedad en el ritmo según necesidades narrativas\n"
        
        instructions += "\n"
        
        # Instrucciones según profundidad temática
        if thematic_depth == "philosophical":
            instructions += "- Los temas filosóficos deben estar presentes desde el outline\n"
            instructions += "- Incluye dilemas morales complejos en los key_events\n"
            instructions += "- Los arcos de personajes deben explorar preguntas existenciales\n"
        elif thematic_depth == "deconstructive":
            instructions += "- Permite subversión de expectativas de género\n"
            instructions += "- Los eventos pueden desafiar convenciones narrativas\n"
            instructions += "- Ambigüedad y complejidad moral son bienvenidas\n"
        elif thematic_depth == "entertainment":
            instructions += "- Enfoque en eventos emocionantes y satisfactorios\n"
            instructions += "- Temas claros y accesibles\n"
            instructions += "- Arcos completos y resoluciones satisfactorias\n"
        
        return instructions + "\n"
    
    def _build_page_writing_instructions(self, page_number: int, total_pages: int) -> str:
        """Construye instrucciones específicas para escribir una página."""
        
        prose_complexity = self.dimensions.get('prose_complexity', 'moderate')
        description_level = self.dimensions.get('description_level', 'selective')
        dialogue_style = self.dimensions.get('dialogue_style', 'natural')
        
        instructions = "**INSTRUCCIONES DE ESCRITURA:**\n\n"
        
        # Instrucciones según complejidad de prosa
        prose_info = get_dimension_info('prose_complexity', prose_complexity)
        if prose_info:
            instructions += f"**Estilo de Prosa:** {prose_info.get('name')}\n"
            for char in prose_info.get('characteristics', [])[:3]:
                instructions += f"  • {char}\n"
            instructions += "\n"
        
        # Instrucciones según nivel de descripción
        desc_info = get_dimension_info('description_level', description_level)
        if desc_info:
            instructions += f"**Nivel de Descripción:** {desc_info.get('name')}\n"
            for char in desc_info.get('characteristics', [])[:3]:
                instructions += f"  • {char}\n"
            instructions += "\n"
        
        # Instrucciones según estilo de diálogo
        dialogue_info = get_dimension_info('dialogue_style', dialogue_style)
        if dialogue_info:
            instructions += f"**Estilo de Diálogo:** {dialogue_info.get('name')}\n"
            for char in dialogue_info.get('characteristics', [])[:2]:
                instructions += f"  • {char}\n"
            instructions += "\n"
        
        # Instrucciones especiales según progreso en el capítulo
        if page_number == 1:
            instructions += "**NOTA:** Esta es la primera página del capítulo. Establece la escena y el tono.\n\n"
        elif page_number == total_pages:
            instructions += "**NOTA:** Esta es la última página del capítulo. Concluye la escena actual y prepara la transición.\n\n"
        elif page_number > total_pages * 0.7:
            instructions += "**NOTA:** Estás cerca del final del capítulo. Comienza a resolver o escalar los conflictos principales.\n\n"
        
        # Agregar ejemplos si existen
        if self.examples:
            instructions += "**EJEMPLOS DE ESTILO:**\n\n"
            for example in self.examples[:2]:  # Máximo 2 ejemplos
                instructions += f"{example}\n\n"
        
        return instructions
    
    def _build_length_instruction(self, page_number: int, total_pages: int) -> str:
        """Determina la longitud objetivo según el estilo."""
        
        # Ajustar longitud según densidad narrativa
        narrative_density = self.dimensions.get('narrative_density', 'balanced')
        
        if narrative_density == "fast_paced":
            min_words, max_words = 350, 450
        elif narrative_density in ["contemplative", "epic"]:
            min_words, max_words = 500, 650
        else:  # balanced
            min_words, max_words = 400, 550
        
        return f"""**LONGITUD OBJETIVO:** 
Escribe entre {min_words} y {max_words} palabras para esta página.
Continúa DIRECTAMENTE desde el último fragmento escrito, sin repetir contenido.

**IMPORTANTE:** 
- NO incluyas títulos de capítulo (ya están en el manuscrito)
- NO repitas el último párrafo escrito
- Comienza inmediatamente con la continuación de la narrativa
"""
    
    def _format_key_events(self, key_events: List[str]) -> str:
        """Formatea la lista de eventos clave."""
        if not key_events:
            return "No se especificaron eventos clave"
        
        formatted = ""
        for i, event in enumerate(key_events, 1):
            formatted += f"  {i}. {event}\n"
        return formatted.strip()
    
    # ========================================================================
    # PROMPTS AUXILIARES
    # ========================================================================
    
    def build_character_update_prompt(self, 
                                     chapter_content: str,
                                     character_names: List[str]) -> str:
        """
        Construye prompt para actualizar estados de personajes.
        
        Args:
            chapter_content: Contenido del capítulo completado
            character_names: Lista de nombres de personajes
            
        Returns:
            Prompt para actualización
        """
        
        prompt = f"""Analiza el contenido del capítulo y actualiza el estado de los personajes mencionados.

**CONTENIDO DEL CAPÍTULO (últimas 2000 palabras):**
{chapter_content[-2000:]}

**PERSONAJES A ACTUALIZAR:**
{', '.join(character_names)}

**INSTRUCCIONES:**
Describe el nuevo estado de cada personaje de forma CONCISA (máximo 1-2 líneas por personaje).
Enfócate en:
- Cambios emocionales significativos
- Nuevas motivaciones o decisiones
- Relaciones afectadas
- Estado físico si es relevante

**FORMATO DE RESPUESTA (JSON):**
```json
{{
    "character_updates": {{
        "Nombre": "Estado actual breve y concreto"
    }}
}}
```

Responde ÚNICAMENTE con el JSON.
"""
        return prompt
    
    def build_blurb_prompt(self, book_metadata: Dict[str, Any]) -> str:
        """
        Construye prompt para generar el blurb de contraportada.
        
        Args:
            book_metadata: Metadatos del libro
            
        Returns:
            Prompt para generar blurb
        """
        
        prompt = f"""Actúa como un editor experto en marketing editorial.

Escribe un resumen de contraportada (blurb) intrigante y comercial para la siguiente novela:

**INFORMACIÓN DEL LIBRO:**
- **Título:** {book_metadata.get('title', 'Sin Título')}
- **Estilo:** {book_metadata.get('author_style', 'neutral')}
- **Premisa:** {book_metadata.get('premise', '')}
- **Temas:** {', '.join(book_metadata.get('themes', []))}

**INSTRUCCIONES:**
- Tono: Intrigante y atrapante, apropiado para el género
- Longitud: 150-200 palabras
- NO reveles el final ni giros importantes
- Enfócate en el gancho emocional y el conflicto principal
- Termina con una pregunta o situación que genere curiosidad

Responde ÚNICAMENTE con el texto del blurb, sin formato adicional.
"""
        return prompt