"""
Instrucciones específicas de escritura por tipo de contenido.
Estas se combinan con los templates según el contexto.
"""

from typing import Dict, List


class WritingInstructions:
    """
    Colección de instrucciones de escritura específicas.
    Se adaptan según el contexto (inicio de capítulo, final, acción, etc.)
    """
    
    # ========================================================================
    # INSTRUCCIONES POR POSICIÓN EN CAPÍTULO
    # ========================================================================
    
    @staticmethod
    def chapter_opening() -> str:
        """Instrucciones para la primera página de un capítulo."""
        return """
**APERTURA DE CAPÍTULO:**
- Establece el escenario y el tono inmediatamente
- Si hay cambio de tiempo/lugar, aclararlo sutilmente
- Engancha al lector desde la primera línea
- Puede comenzar in medias res o con atmósfera, según el estilo
"""
    
    @staticmethod
    def chapter_middle(progress: float) -> str:
        """
        Instrucciones para páginas intermedias.
        
        Args:
            progress: Progreso en el capítulo (0.0 a 1.0)
        """
        if progress < 0.3:
            return """
**DESARROLLO INICIAL:**
- Desarrolla la escena establecida al inicio
- Introduce o profundiza conflictos
- Avanza eventos según el outline del capítulo
"""
        elif progress < 0.7:
            return """
**DESARROLLO MEDIO:**
- Punto de mayor intensidad del capítulo
- Desarrolla eventos clave planificados
- Mantén la tensión narrativa
- Profundiza en las reacciones de los personajes
"""
        else:
            return """
**APROXIMACIÓN AL CIERRE:**
- Comienza a resolver o escalar los conflictos del capítulo
- Prepara la transición hacia el cierre
- Mantén el momentum narrativo
"""
    
    @staticmethod
    def chapter_closing() -> str:
        """Instrucciones para la última página de un capítulo."""
        return """
**CIERRE DE CAPÍTULO:**
- Concluye la escena o secuencia actual
- Puede incluir un gancho sutil para el siguiente capítulo
- Deja una imagen o emoción resonante
- Asegura transición natural hacia el siguiente capítulo
"""
    
    # ========================================================================
    # INSTRUCCIONES POR TIPO DE ESCENA
    # ========================================================================
    
    @staticmethod
    def action_scene() -> str:
        """Instrucciones para escenas de acción."""
        return """
**ESCENA DE ACCIÓN:**
- Oraciones más cortas para aumentar el ritmo
- Verbos de acción potentes y específicos
- Descripciones precisas pero rápidas
- Mantén claridad espacial (dónde está cada personaje)
- Sensaciones físicas inmediatas
"""
    
    @staticmethod
    def dialogue_scene() -> str:
        """Instrucciones para escenas con diálogo predominante."""
        return """
**ESCENA DE DIÁLOGO:**
- Cada personaje debe tener voz distintiva
- Incluye beats (acciones pequeñas) entre diálogos
- Subtexto: lo no dicho es tan importante como lo dicho
- Evita diálogos "on the nose" (demasiado directos)
- Tags de diálogo variados pero no rebuscados
"""
    
    @staticmethod
    def introspection_scene() -> str:
        """Instrucciones para escenas introspectivas."""
        return """
**ESCENA INTROSPECTIVA:**
- Permite profundizar en los pensamientos del personaje
- Conecta emociones actuales con eventos pasados si es relevante
- Mantén anclaje al presente (sensaciones físicas, entorno)
- Evita que se vuelva puramente expositivo
- Debe haber tensión interna o conflicto
"""
    
    @staticmethod
    def descriptive_scene() -> str:
        """Instrucciones para escenas descriptivas/atmosféricas."""
        return """
**ESCENA DESCRIPTIVA:**
- Involucra múltiples sentidos (vista, oído, olfato, tacto)
- Conecta la descripción con las emociones de los personajes
- Usa detalles específicos y evocadores
- La descripción debe servir al mood de la escena
- No detengas completamente la narrativa
"""
    
    # ========================================================================
    # INSTRUCCIONES DE CONTINUIDAD
    # ========================================================================
    
    @staticmethod
    def continuity_reminders() -> str:
        """Recordatorios generales de continuidad."""
        return """
**RECORDATORIOS DE CONTINUIDAD:**
- Mantén consistencia con lo establecido previamente
- Respeta la personalidad y motivaciones de los personajes
- Los eventos deben tener consecuencias
- El tiempo debe fluir lógicamente
- Elementos del worldbuilding deben ser consistentes
"""
    
    @staticmethod
    def pacing_awareness(current_pace: str) -> str:
        """
        Instrucciones sobre ritmo.
        
        Args:
            current_pace: 'slow', 'moderate', 'fast'
        """
        if current_pace == 'fast':
            return """
**RITMO RÁPIDO:**
- Enfócate en acción y eventos
- Transiciones rápidas entre momentos
- Descripciones funcionales y breves
- Diálogos concisos
"""
        elif current_pace == 'slow':
            return """
**RITMO LENTO:**
- Permite momentos de reflexión
- Descripciones más elaboradas
- Desarrollo emocional profundo
- Atmósfera detallada
"""
        else:
            return """
**RITMO MODERADO:**
- Balance entre acción y reflexión
- Variación de velocidad según la escena
- Descripciones selectivas
- Mix de diálogo y narrativa
"""
    
    # ========================================================================
    # INSTRUCCIONES DE CALIDAD
    # ========================================================================
    
    @staticmethod
    def quality_checklist() -> str:
        """Checklist de calidad para el contenido generado."""
        return """
**CHECKLIST DE CALIDAD:**
✓ ¿Los eventos avanzan la trama?
✓ ¿Los personajes actúan de forma consistente?
✓ ¿Hay tensión o conflicto presente?
✓ ¿Las descripciones son evocadoras, no solo informativas?
✓ ¿Los diálogos suenan naturales?
✓ ¿El ritmo es apropiado para la escena?
✓ ¿Se respetan las reglas del mundo establecidas?
"""
    
    @staticmethod
    def show_dont_tell() -> str:
        """Recordatorio de mostrar vs. contar."""
        return """
**MOSTRAR VS. CONTAR:**
- Prefiere MOSTRAR emociones a través de acciones y sensaciones físicas
- CUENTA solo cuando necesites resumir o transicionar rápidamente
- Ejemplo de MOSTRAR: "Sus manos temblaban mientras alcanzaba la manija"
- Ejemplo de CONTAR: "Estaba nervioso"
"""
    
    # ========================================================================
    # INSTRUCCIONES COMBINADAS
    # ========================================================================
    
    @staticmethod
    def get_contextual_instructions(page_position: str,
                                   scene_type: str,
                                   pace: str) -> str:
        """
        Combina instrucciones según contexto.
        
        Args:
            page_position: 'opening', 'middle', 'closing'
            scene_type: 'action', 'dialogue', 'introspection', 'descriptive', 'mixed'
            pace: 'slow', 'moderate', 'fast'
            
        Returns:
            Instrucciones combinadas relevantes
        """
        instructions = []
        
        # Instrucciones de posición
        if page_position == 'opening':
            instructions.append(WritingInstructions.chapter_opening())
        elif page_position == 'closing':
            instructions.append(WritingInstructions.chapter_closing())
        else:
            # Para middle, necesitamos el progreso, usar default
            instructions.append(WritingInstructions.chapter_middle(0.5))
        
        # Instrucciones de tipo de escena
        if scene_type == 'action':
            instructions.append(WritingInstructions.action_scene())
        elif scene_type == 'dialogue':
            instructions.append(WritingInstructions.dialogue_scene())
        elif scene_type == 'introspection':
            instructions.append(WritingInstructions.introspection_scene())
        elif scene_type == 'descriptive':
            instructions.append(WritingInstructions.descriptive_scene())
        
        # Instrucciones de ritmo
        instructions.append(WritingInstructions.pacing_awareness(pace))
        
        # Siempre incluir continuidad
        instructions.append(WritingInstructions.continuity_reminders())
        
        return "\n".join(instructions)