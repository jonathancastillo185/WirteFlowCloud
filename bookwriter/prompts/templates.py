"""
Templates base para diferentes tipos de prompts.
Estos templates son independientes del estilo y se llenan con datos específicos.
"""

from typing import Dict, Any, List


class PromptTemplates:
    """
    Colección de templates de prompts reutilizables.
    Separa la estructura del prompt de los datos específicos.
    """
    
    # ========================================================================
    # TEMPLATE: SYSTEM PROMPT BASE
    # ========================================================================
    
    @staticmethod
    def system_base(author_style: str, 
                   title: str, 
                   premise: str, 
                   themes: List[str]) -> str:
        """Template base para el prompt del sistema."""
        
        themes_str = ', '.join(themes) if themes else 'A desarrollar'
        
        return f"""Eres un escritor experto en el estilo de {author_style}.

**INFORMACIÓN DE LA NOVELA:**
- **Título:** {title}
- **Premisa:** {premise}
- **Temas:** {themes_str}

Tu objetivo es crear una narrativa consistente, envolvente y fiel al estilo literario establecido.
"""
    
    # ========================================================================
    # TEMPLATE: OUTLINE GENERATION
    # ========================================================================
    
    @staticmethod
    def outline_generation(premise: str,
                          num_chapters: int,
                          themes: str,
                          author_style: str) -> str:
        """Template para generación de outline."""
        
        return f"""Basado en la siguiente información, genera un outline detallado para una novela de {num_chapters} capítulos.

**PREMISA:** {premise}
**TEMAS:** {themes}
**ESTILO:** {author_style}

El outline debe incluir:
- Worldbuilding detallado (escenario, período, ubicaciones clave, reglas del mundo)
- Personajes principales con descripciones completas y arcos de desarrollo
- Estructura narrativa con resumen de cada capítulo
- Eventos clave por capítulo
- Estimación de páginas por capítulo
- Reglas de consistencia para mantener coherencia

"""
    
    @staticmethod
    def outline_json_structure() -> str:
        """Estructura JSON requerida para el outline."""
        
        return """
**ESTRUCTURA JSON REQUERIDA:**
```json
{
    "world": {
        "setting": "Descripción del escenario principal",
        "time_period": "Período temporal",
        "key_locations": {
            "Lugar 1": "Descripción detallada",
            "Lugar 2": "Descripción detallada"
        },
        "rules_of_the_world": [
            "Regla fundamental 1",
            "Regla fundamental 2"
        ]
    },
    "characters": {
        "Nombre Completo": {
            "description": "Descripción física y de fondo (2-3 oraciones)",
            "personality": "Rasgos de personalidad clave",
            "story_arc": "Evolución a lo largo de la historia",
            "relationships": "Conexiones con otros personajes",
            "internal_conflict": "Conflicto interno principal",
            "external_goal": "Objetivo externo que persigue"
        }
    },
    "style": {
        "tone": "Tono general de la narrativa",
        "point_of_view": "Primera persona / Tercera persona limitada / Tercera persona omnisciente",
        "tense": "Presente / Pasado"
    },
    "plot": {
        "outline": [
            {
                "number": 1,
                "title": "Título descriptivo del capítulo",
                "summary": "Resumen de eventos principales (3-4 oraciones)",
                "key_events": [
                    "Evento específico 1",
                    "Evento específico 2",
                    "Evento específico 3"
                ],
                "character_focus": ["Personaje 1", "Personaje 2"],
                "emotional_arc": "Progresión emocional del capítulo",
                "thematic_focus": "Tema principal explorado",
                "pages_estimate": 12
            }
        ]
    },
    "consistency_rules": [
        "Regla de consistencia 1 (ej: 'La magia requiere un costo físico')",
        "Regla de consistencia 2 (ej: 'Los diálogos deben reflejar el origen social')"
    ]
}
```

**IMPORTANTE:** 
- Tu respuesta debe ser ÚNICAMENTE el JSON válido
- Sin texto adicional antes o después del JSON
- Sin bloques de código markdown (```json)
- Asegúrate de que todos los corchetes y llaves estén balanceados
"""
    
    # ========================================================================
    # TEMPLATE: PAGE GENERATION
    # ========================================================================
    
    @staticmethod
    def page_context(chapter_number: int,
                    chapter_title: str,
                    chapter_summary: str,
                    key_events: List[str],
                    page_number: int,
                    total_pages: int) -> str:
        """Template para contexto de página."""
        
        events_formatted = "\n".join([f"  {i}. {event}" for i, event in enumerate(key_events, 1)])
        
        return f"""Estás escribiendo la página {page_number} de {total_pages} del siguiente capítulo:

**CAPÍTULO {chapter_number}: "{chapter_title}"**

**EVENTOS QUE DEBEN OCURRIR EN ESTE CAPÍTULO:**
{chapter_summary}

**EVENTOS CLAVE:**
{events_formatted if events_formatted else "  (No especificados)"}

"""
    
    @staticmethod
    def character_context(character_profiles: str) -> str:
        """Template para contexto de personajes."""
        
        if not character_profiles or character_profiles.strip() == "":
            return "**PERSONAJES EN ESCENA:**\nNo hay personajes específicos en foco para esta página.\n\n"
        
        return f"""**PERSONAJES EN ESCENA:**
{character_profiles}

"""
    
    @staticmethod
    def relevant_context(context: str) -> str:
        """Template para contexto de memoria semántica."""
        
        if not context or "No hay contexto disponible" in context:
            return ""
        
        return f"""**CONTEXTO RELEVANTE DE CAPÍTULOS ANTERIORES:**
{context}

"""
    
    @staticmethod
    def continuation_context(last_text: str, is_chapter_start: bool = False) -> str:
        """Template para contexto de continuación."""
        
        if is_chapter_start:
            return "**[INICIO DEL CAPÍTULO]**\n\n"
        
        if not last_text:
            return "**[INICIO DE LA NARRATIVA]**\n\n"
        
        return f"""**ÚLTIMO FRAGMENTO ESCRITO (Continúa DIRECTAMENTE desde aquí):**
...{last_text}

"""
    
    @staticmethod
    def length_instruction(min_words: int, max_words: int) -> str:
        """Template para instrucciones de longitud."""
        
        return f"""

**LONGITUD OBJETIVO:** 
Escribe entre {min_words} y {max_words} palabras para esta página.

**IMPORTANTE:** 
- NO incluyas títulos de capítulo (ya están en el manuscrito)
- NO repitas el último párrafo escrito
- Comienza inmediatamente con la continuación de la narrativa
- Mantén el flujo natural desde el último fragmento
"""
    
    # ========================================================================
    # TEMPLATE: CHARACTER UPDATE
    # ========================================================================
    
    @staticmethod
    def character_update(chapter_content: str,
                        character_names: List[str]) -> str:
        """Template para actualización de personajes."""
        
        names_str = ', '.join(character_names)
        
        return f"""Analiza el contenido del capítulo completado y actualiza el estado de los personajes mencionados.

**CONTENIDO DEL CAPÍTULO (últimas 2000 palabras):**
{chapter_content[-2000:]}

**PERSONAJES A ACTUALIZAR:**
{names_str}

**INSTRUCCIONES:**
Para cada personaje, describe su nuevo estado de forma CONCISA (máximo 1-2 líneas).
Enfócate en:
- Cambios emocionales significativos
- Nuevas motivaciones o decisiones tomadas
- Relaciones afectadas o nuevas dinámicas
- Estado físico relevante (heridas, cansancio, etc.)
- Conocimiento nuevo adquirido

**FORMATO DE RESPUESTA (JSON):**
```json
{{
    "character_updates": {{
        "Nombre Personaje": "Descripción breve y concreta del estado actual"
    }}
}}
```

Responde ÚNICAMENTE con el JSON válido, sin texto adicional.
"""
    
    # ========================================================================
    # TEMPLATE: BLURB GENERATION
    # ========================================================================
    
    @staticmethod
    def blurb_generation(title: str,
                        author_style: str,
                        premise: str,
                        themes: List[str]) -> str:
        """Template para generación de blurb."""
        
        themes_str = ', '.join(themes) if themes else 'Diversos'
        
        return f"""Actúa como un editor experto en marketing editorial.

Escribe un resumen de contraportada (blurb) intrigante y comercial para la siguiente novela:

**INFORMACIÓN DEL LIBRO:**
- **Título:** {title}
- **Estilo Literario:** {author_style}
- **Premisa:** {premise}
- **Temas Principales:** {themes_str}

**INSTRUCCIONES:**
1. **Tono:** Intrigante, atrapante y apropiado para el género
2. **Longitud:** 150-200 palabras
3. **Estructura sugerida:**
   - Hook inicial (1-2 oraciones que capten la atención)
   - Presentación del conflicto o situación principal
   - Sugerencia de stakes y tensión
   - Cierre con pregunta o situación que genere curiosidad
4. **Evita:**
   - Revelar el final o giros importantes
   - Spoilers de eventos clave
   - Detalles excesivos de la trama
5. **Enfócate en:**
   - El gancho emocional
   - El conflicto principal
   - Lo que hace única a esta historia

Responde ÚNICAMENTE con el texto del blurb, sin formato adicional, sin comillas, sin introducción.
"""
    
    # ========================================================================
    # TEMPLATE: COVER PROMPT GENERATION
    # ========================================================================
    
    @staticmethod
    def cover_art_prompt(title: str,
                        author_style: str,
                        blurb: str,
                        themes: List[str]) -> str:
        """Template para generación de prompt de portada."""
        
        themes_str = ', '.join(themes) if themes else 'Diversos'
        
        return f"""Actúa como un director de arte especializado en portadas de libros.

Basado en los siguientes detalles, crea un prompt descriptivo para un modelo de IA de texto a imagen (text-to-image).

**INFORMACIÓN DEL LIBRO:**
- **Título:** {title}
- **Estilo Literario:** {author_style}
- **Resumen:** {blurb}
- **Temas:** {themes_str}

**INSTRUCCIONES:**

1. **Tipo de Imagen:**
   - Puede ser una escena evocadora, un paisaje onírico, un retrato atmosférico, o arte abstracto
   - Debe capturar la ESENCIA y MOOD de la historia
   - Apropiada para una portada de libro profesional

2. **Estilo Visual:**
   - Considera estilos como: pintura al óleo clásica, arte digital épico, acuarela atmosférica, ilustración gótica, arte conceptual cinematográfico, etc.
   - Elige el estilo que mejor represente el tono del libro

3. **Elementos Técnicos:**
   - Usa adjetivos POTENTES para iluminación (ej: "dramatic chiaroscuro lighting", "ethereal golden hour glow")
   - Especifica paleta de colores (ej: "muted earth tones", "vibrant neon colors", "desaturated cold blues")
   - Define atmósfera (ej: "oppressive atmosphere", "dreamlike quality", "tense and claustrophobic")

4. **CRÍTICO:**
   - El prompt final DEBE estar escrito en INGLÉS
   - Longitud: 2-4 oraciones descriptivas
   - Evita incluir texto o letras en la imagen

5. **Formato:**
   Escribe el prompt de forma directa, sin introducción ni explicaciones adicionales.

**EJEMPLO DE FORMATO:**
"A desolate cyberpunk cityscape at twilight, towering neon-lit skyscrapers pierce through thick smog, dramatic rain-soaked streets reflect pink and blue lights, lonely figure in silhouette, digital painting style, cinematic composition, moody atmospheric lighting, 8k detail."

Responde ÚNICAMENTE con el prompt en inglés.
"""
    
    # ========================================================================
    # TEMPLATE: CHAPTER SUMMARY
    # ========================================================================
    
    @staticmethod
    def chapter_summary_request(chapter_number: int,
                               chapter_title: str,
                               chapter_content: str) -> str:
        """Template para solicitar resumen de capítulo."""
        
        return f"""Resume el contenido del siguiente capítulo de forma concisa.

**CAPÍTULO {chapter_number}: "{chapter_title}"**

**CONTENIDO:**
{chapter_content}

**INSTRUCCIONES:**
Escribe un resumen de 3-5 oraciones que capture:
- Los eventos principales que ocurrieron
- Desarrollo de personajes significativo
- Progresión de la trama
- Momento emocional clave

Responde ÚNICAMENTE con el resumen, sin introducción.
"""
    
    # ========================================================================
    # TEMPLATE: ERROR MESSAGES
    # ========================================================================
    
    @staticmethod
    def error_missing_outline() -> str:
        """Mensaje de error cuando no hay outline."""
        return "⚠️ No se ha generado un outline para este proyecto. Por favor, genera el outline primero."
    
    @staticmethod
    def error_invalid_chapter() -> str:
        """Mensaje de error para capítulo inválido."""
        return "⚠️ Índice de capítulo inválido o fuera de rango."
    
    @staticmethod
    def error_api_failure(service: str, error: str) -> str:
        """Mensaje de error para fallas de API."""
        return f"❌ Error en la llamada a {service}: {error}"
    
    @staticmethod
    def error_json_parse(raw_response: str) -> str:
        """Mensaje de error para falla en parseo JSON."""
        return f"""❌ Error al procesar la respuesta del modelo.
La respuesta no es un JSON válido.

**Primeros 500 caracteres de la respuesta:**
{raw_response[:500]}...

Por favor, intenta regenerar el outline.
"""