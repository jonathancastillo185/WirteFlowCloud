"""
Validador de consistencia narrativa.
Verifica que la historia mantenga coherencia interna.
"""

from typing import Dict, Any, List, Tuple, Set
import re


class ConsistencyValidator:
    """
    Valida la consistencia interna de la narrativa.
    Detecta contradicciones y problemas de continuidad.
    """
    
    # ========================================================================
    # VALIDACIÓN DE PERSONAJES
    # ========================================================================
    
    @staticmethod
    def validate_character_consistency(character_name: str,
                                       original_data: Dict[str, Any],
                                       state_history: List[str]) -> Tuple[bool, List[str]]:
        """
        Valida que un personaje mantenga consistencia.
        
        Args:
            character_name: Nombre del personaje
            original_data: Datos originales del personaje
            state_history: Historial de estados del personaje
            
        Returns:
            Tupla (consistente: bool, lista de problemas: List[str])
        """
        
        problems = []
        
        # Verificar que el estado actual exista
        if 'current_state' not in original_data:
            problems.append(f"{character_name}: Falta estado actual")
        
        # Verificar cambios drásticos sin justificación
        if len(state_history) > 1:
            for i in range(len(state_history) - 1):
                prev_state = state_history[i].lower()
                next_state = state_history[i + 1].lower()
                
                # Detectar cambios contradictorios
                contradictions = ConsistencyValidator._detect_contradictions(prev_state, next_state)
                if contradictions:
                    problems.append(f"{character_name}: Posible contradicción entre estados {i+1} y {i+2}: {contradictions}")
        
        is_consistent = len(problems) == 0
        
        return is_consistent, problems
    
    @staticmethod
    def _detect_contradictions(state1: str, state2: str) -> str:
        """Detecta contradicciones entre dos estados."""
        
        # Pares contradictorios
        contradictions = [
            (['muerto', 'murió', 'fallecido'], ['vivo', 'despierto', 'consciente']),
            (['feliz', 'alegre', 'contento'], ['triste', 'deprimido', 'desesperado']),
            (['confiado', 'seguro'], ['inseguro', 'temeroso']),
            (['herido', 'lastimado'], ['sano', 'ileso', 'recuperado'])
        ]
        
        for group1, group2 in contradictions:
            has_state1_g1 = any(word in state1 for word in group1)
            has_state1_g2 = any(word in state1 for word in group2)
            has_state2_g1 = any(word in state2 for word in group1)
            has_state2_g2 = any(word in state2 for word in group2)
            
            # Si estado 1 tiene grupo1 y estado 2 tiene grupo2, o viceversa
            if (has_state1_g1 and has_state2_g2) or (has_state1_g2 and has_state2_g1):
                return f"Cambio de {group1[0]} a {group2[0]} sin transición"
        
        return ""
    
    # ========================================================================
    # VALIDACIÓN DE WORLDBUILDING
    # ========================================================================
    
    @staticmethod
    def validate_world_consistency(world_data: Dict[str, Any],
                                   consistency_rules: List[str]) -> Tuple[bool, List[str]]:
        """
        Valida que el worldbuilding mantenga consistencia.
        
        Args:
            world_data: Datos del mundo
            consistency_rules: Reglas de consistencia establecidas
            
        Returns:
            Tupla (consistente: bool, lista de problemas: List[str])
        """
        
        problems = []
        
        # Verificar que existan las ubicaciones clave
        if 'key_locations' not in world_data:
            problems.append("World: Falta definición de ubicaciones clave")
        else:
            locations = world_data['key_locations']
            if not isinstance(locations, dict) or len(locations) == 0:
                problems.append("World: No hay ubicaciones definidas")
        
        # Verificar reglas del mundo
        if 'rules_of_the_world' not in world_data:
            problems.append("World: Falta definición de reglas del mundo")
        else:
            rules = world_data['rules_of_the_world']
            if not isinstance(rules, list) or len(rules) == 0:
                problems.append("World: No hay reglas del mundo definidas")
        
        is_consistent = len(problems) == 0
        
        return is_consistent, problems
    
    # ========================================================================
    # VALIDACIÓN DE PROGRESO NARRATIVO
    # ========================================================================
    
    @staticmethod
    def validate_narrative_progress(chapter_summaries: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        Valida que la narrativa progrese lógicamente.
        
        Args:
            chapter_summaries: Lista de resúmenes de capítulos
            
        Returns:
            Tupla (válido: bool, lista de problemas: List[str])
        """
        
        problems = []
        
        if not chapter_summaries or len(chapter_summaries) == 0:
            problems.append("No hay capítulos para validar progreso")
            return False, problems
        
        # Verificar que los números de capítulo sean consecutivos
        for i, summary in enumerate(chapter_summaries):
            expected_num = i + 1
            actual_num = summary.get('number', -1)
            
            if actual_num != expected_num:
                problems.append(f"Capítulo {i+1}: Número incorrecto (esperado {expected_num}, encontrado {actual_num})")
        
        # Detectar capítulos sin progreso significativo
        for i, summary in enumerate(chapter_summaries):
            summary_text = summary.get('summary', '')
            if len(summary_text) < 20:
                problems.append(f"Capítulo {i+1}: Resumen vacío o insuficiente")
        
        is_valid = len(problems) == 0
        
        return is_valid, problems
    
    # ========================================================================
    # VALIDACIÓN DE TIMELINE
    # ========================================================================
    
    @staticmethod
    def validate_timeline(chapters: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        Valida la línea temporal de la historia.
        
        Args:
            chapters: Lista de capítulos con información temporal
            
        Returns:
            Tupla (válido: bool, lista de problemas: List[str])
        """
        
        problems = []
        
        # Extraer referencias temporales
        temporal_refs = []
        
        for i, chapter in enumerate(chapters, 1):
            summary = chapter.get('summary', '').lower()
            
            # Buscar referencias temporales
            time_patterns = [
                r'(\d+)\s+(días?|semanas?|meses?|años?)',
                r'(ayer|hoy|mañana|anoche)',
                r'(pasado|presente|futuro)'
            ]
            
            for pattern in time_patterns:
                matches = re.findall(pattern, summary)
                if matches:
                    temporal_refs.append({
                        'chapter': i,
                        'reference': matches[0] if isinstance(matches[0], str) else ' '.join(matches[0])
                    })
        
        # Por ahora, solo registramos las referencias encontradas
        # En una implementación más avanzada, se podría validar la coherencia temporal
        
        if len(temporal_refs) > 0:
            # Al menos hay referencias temporales
            pass
        
        is_valid = len(problems) == 0
        
        return is_valid, problems
    
    # ========================================================================
    # VALIDACIÓN DE MENCIONES
    # ========================================================================
    
    @staticmethod
    def validate_character_mentions(content: str,
                                   expected_characters: Set[str],
                                   chapter_number: int) -> Tuple[bool, List[str]]:
        """
        Valida que los personajes mencionados estén definidos.
        
        Args:
            content: Contenido del capítulo
            expected_characters: Set de nombres de personajes esperados
            chapter_number: Número del capítulo
            
        Returns:
            Tupla (válido: bool, lista de advertencias: List[str])
        """
        
        warnings = []
        
        # Buscar nombres propios (palabras que empiezan con mayúscula)
        potential_names = re.findall(r'\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\b', content)
        
        # Filtrar nombres comunes que no son personajes
        common_words = {'El', 'La', 'Los', 'Las', 'Un', 'Una', 'Algunos', 'Muchos'}
        potential_names = [name for name in potential_names if name not in common_words]
        
        # Contar frecuencia
        from collections import Counter
        name_freq = Counter(potential_names)
        
        # Detectar nombres frecuentes no definidos
        for name, count in name_freq.items():
            if count >= 3:  # Mencionado al menos 3 veces
                if name not in expected_characters:
                    warnings.append(f"Capítulo {chapter_number}: '{name}' mencionado {count} veces pero no está en la lista de personajes")
        
        is_valid = len(warnings) == 0
        
        return is_valid, warnings
    
    # ========================================================================
    # REPORTE DE CONSISTENCIA
    # ========================================================================
    
    @staticmethod
    def generate_consistency_report(memory: Dict[str, Any]) -> str:
        """
        Genera un reporte completo de consistencia.
        
        Args:
            memory: Memoria completa del proyecto
            
        Returns:
            Reporte formateado
        """
        
        report = "📊 REPORTE DE CONSISTENCIA\n"
        report += "=" * 60 + "\n\n"
        
        # Validar worldbuilding
        world = memory.get('world', {})
        world_valid, world_problems = ConsistencyValidator.validate_world_consistency(
            world, memory.get('consistency_rules', [])
        )
        
        report += "🌍 WORLDBUILDING:\n"
        if world_valid:
            report += "   ✅ Consistente\n"
        else:
            report += "   ⚠️ Problemas encontrados:\n"
            for problem in world_problems:
                report += f"      - {problem}\n"
        report += "\n"
        
        # Validar personajes
        characters = memory.get('characters', {})
        report += f"👥 PERSONAJES ({len(characters)}):\n"
        
        for char_name, char_data in characters.items():
            state_history = char_data.get('state_history', [char_data.get('current_state', '')])
            char_valid, char_problems = ConsistencyValidator.validate_character_consistency(
                char_name, char_data, state_history
            )
            
            if char_valid:
                report += f"   ✅ {char_name}: Consistente\n"
            else:
                report += f"   ⚠️ {char_name}:\n"
                for problem in char_problems:
                    report += f"      - {problem}\n"
        
        report += "\n"
        
        # Validar progreso narrativo
        chapters_summary = memory.get('chapters_summary', [])
        if chapters_summary:
            narrative_valid, narrative_problems = ConsistencyValidator.validate_narrative_progress(
                chapters_summary
            )
            
            report += "📖 PROGRESO NARRATIVO:\n"
            if narrative_valid:
                report += "   ✅ Progresión lógica\n"
            else:
                report += "   ⚠️ Problemas:\n"
                for problem in narrative_problems:
                    report += f"      - {problem}\n"
        
        return report
