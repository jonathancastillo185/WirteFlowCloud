"""
Validador de contenido generado.
Verifica la calidad y coherencia del contenido producido por la IA.
"""

import re
from typing import Dict, Any, List, Tuple, Optional


class ContentValidator:
    """
    Valida el contenido generado por la IA.
    Detecta problemas comunes y proporciona retroalimentación.
    """
    
    # ========================================================================
    # VALIDACIÓN DE OUTLINE
    # ========================================================================
    
    @staticmethod
    def validate_outline_structure(outline_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida la estructura completa del outline.
        
        Args:
            outline_data: Datos del outline a validar
            
        Returns:
            Tupla (válido: bool, lista de problemas: List[str])
        """
        
        problems = []
        
        # Verificar secciones principales
        required_sections = ['world', 'characters', 'plot', 'style', 'consistency_rules']
        for section in required_sections:
            if section not in outline_data:
                problems.append(f"Falta sección requerida: '{section}'")
        
        if problems:
            return False, problems
        
        # Validar world
        world_problems = ContentValidator._validate_world_section(outline_data.get('world', {}))
        problems.extend(world_problems)
        
        # Validar characters
        char_problems = ContentValidator._validate_characters_section(outline_data.get('characters', {}))
        problems.extend(char_problems)
        
        # Validar plot
        plot_problems = ContentValidator._validate_plot_section(outline_data.get('plot', {}))
        problems.extend(plot_problems)
        
        # Validar style
        style_problems = ContentValidator._validate_style_section(outline_data.get('style', {}))
        problems.extend(style_problems)
        
        is_valid = len(problems) == 0
        
        return is_valid, problems
    
    @staticmethod
    def _validate_world_section(world: Dict[str, Any]) -> List[str]:
        """Valida la sección de worldbuilding."""
        problems = []
        
        if 'setting' not in world or not world['setting']:
            problems.append("World: Falta descripción del setting")
        elif len(world['setting']) < 20:
            problems.append("World: Setting demasiado breve (mínimo 20 caracteres)")
        
        if 'time_period' not in world or not world['time_period']:
            problems.append("World: Falta especificación del período temporal")
        
        return problems
    
    @staticmethod
    def _validate_characters_section(characters: Dict[str, Any]) -> List[str]:
        """Valida la sección de personajes."""
        problems = []
        
        if not characters:
            problems.append("Characters: No hay personajes definidos")
            return problems
        
        required_fields = ['description', 'personality', 'story_arc']
        
        for char_name, char_data in characters.items():
            if not isinstance(char_data, dict):
                problems.append(f"Character '{char_name}': Datos inválidos")
                continue
            
            for field in required_fields:
                if field not in char_data or not char_data[field]:
                    problems.append(f"Character '{char_name}': Falta campo '{field}'")
                elif len(char_data[field]) < 10:
                    problems.append(f"Character '{char_name}': Campo '{field}' demasiado breve")
        
        return problems
    
    @staticmethod
    def _validate_plot_section(plot: Dict[str, Any]) -> List[str]:
        """Valida la sección de trama."""
        problems = []
        
        if 'outline' not in plot:
            problems.append("Plot: Falta el outline de capítulos")
            return problems
        
        outline = plot['outline']
        
        if not isinstance(outline, list) or len(outline) == 0:
            problems.append("Plot: Outline vacío o inválido")
            return problems
        
        # Validar cada capítulo
        for i, chapter in enumerate(outline, 1):
            chapter_problems = ContentValidator._validate_chapter(chapter, i)
            problems.extend(chapter_problems)
        
        return problems
    
    @staticmethod
    def _validate_chapter(chapter: Dict[str, Any], expected_number: int) -> List[str]:
        """Valida un capítulo individual."""
        problems = []
        prefix = f"Capítulo {expected_number}"
        
        required_fields = ['number', 'title', 'summary', 'key_events', 'pages_estimate']
        
        for field in required_fields:
            if field not in chapter:
                problems.append(f"{prefix}: Falta campo '{field}'")
        
        # Validar número
        if 'number' in chapter and chapter['number'] != expected_number:
            problems.append(f"{prefix}: Número incorrecto (esperado {expected_number}, recibido {chapter['number']})")
        
        # Validar título
        if 'title' in chapter:
            if not chapter['title'] or len(chapter['title']) < 3:
                problems.append(f"{prefix}: Título vacío o demasiado corto")
        
        # Validar resumen
        if 'summary' in chapter:
            if not chapter['summary'] or len(chapter['summary']) < 20:
                problems.append(f"{prefix}: Resumen demasiado breve")
        
        # Validar key_events
        if 'key_events' in chapter:
            if not isinstance(chapter['key_events'], list) or len(chapter['key_events']) == 0:
                problems.append(f"{prefix}: Debe tener al menos un evento clave")
        
        # Validar pages_estimate
        if 'pages_estimate' in chapter:
            pages = chapter['pages_estimate']
            if not isinstance(pages, int) or pages < 5 or pages > 30:
                problems.append(f"{prefix}: Estimación de páginas inválida ({pages})")
        
        return problems
    
    @staticmethod
    def _validate_style_section(style: Dict[str, Any]) -> List[str]:
        """Valida la sección de estilo."""
        problems = []
        
        required_fields = ['tone', 'point_of_view', 'tense']
        
        for field in required_fields:
            if field not in style or not style[field]:
                problems.append(f"Style: Falta campo '{field}'")
        
        return problems
    
    # ========================================================================
    # VALIDACIÓN DE PÁGINA GENERADA
    # ========================================================================
    
    @staticmethod
    def validate_page_content(content: str,
                             min_words: int = 300,
                             max_words: int = 700) -> Tuple[bool, List[str]]:
        """
        Valida el contenido de una página generada.
        
        Args:
            content: Contenido a validar
            min_words: Mínimo de palabras esperadas
            max_words: Máximo de palabras esperadas
            
        Returns:
            Tupla (válido: bool, lista de problemas: List[str])
        """
        
        problems = []
        
        # Verificar que no esté vacío
        if not content or not content.strip():
            problems.append("Contenido vacío")
            return False, problems
        
        # Contar palabras
        word_count = len(content.split())
        
        if word_count < min_words:
            problems.append(f"Contenido demasiado corto: {word_count} palabras (mínimo {min_words})")
        
        if word_count > max_words:
            problems.append(f"Contenido demasiado largo: {word_count} palabras (máximo {max_words})")
        
        # Verificar que no tenga marcadores de capítulo
        if re.search(r'^##\s+Cap[íi]tulo', content, re.MULTILINE):
            problems.append("El contenido incluye marcador de capítulo (debe omitirse)")
        
        # Verificar que no tenga bloques de código
        if '```' in content:
            problems.append("El contenido incluye bloques de código markdown")
        
        # Verificar repetición excesiva
        repetition_check = ContentValidator._check_repetition(content)
        if repetition_check:
            problems.append(repetition_check)
        
        # Verificar si parece contenido meta (instrucciones, etc)
        meta_check = ContentValidator._check_meta_content(content)
        if meta_check:
            problems.append(meta_check)
        
        is_valid = len(problems) == 0
        
        return is_valid, problems
    
    @staticmethod
    def _check_repetition(content: str) -> Optional[str]:
        """Detecta repetición excesiva de frases."""
        
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        
        if len(sentences) < 3:
            return None
        
        # Buscar oraciones repetidas
        for i, sent in enumerate(sentences):
            if len(sent) < 20:  # Oraciones muy cortas no cuentan
                continue
            
            # Contar cuántas veces aparece esta oración
            count = sum(1 for s in sentences if s == sent)
            if count > 2:
                return f"Oración repetida {count} veces: '{sent[:50]}...'"
        
        return None
    
    @staticmethod
    def _check_meta_content(content: str) -> Optional[str]:
        """Detecta si el contenido parece meta-instrucciones."""
        
        meta_indicators = [
            'instrucciones:',
            'nota del autor:',
            'este capítulo debe',
            'el personaje debería',
            'la escena debe',
            'importante:',
            'recordatorio:',
            'continúa desde aquí'
        ]
        
        content_lower = content.lower()
        
        for indicator in meta_indicators:
            if indicator in content_lower:
                return f"Contenido parece incluir meta-instrucciones ('{indicator}')"
        
        return None
    
    # ========================================================================
    # VALIDACIÓN DE CALIDAD NARRATIVA
    # ========================================================================
    
    @staticmethod
    def analyze_narrative_quality(content: str) -> Dict[str, Any]:
        """
        Analiza la calidad narrativa del contenido.
        
        Args:
            content: Contenido a analizar
            
        Returns:
            Diccionario con métricas de calidad
        """
        
        analysis = {
            "word_count": len(content.split()),
            "sentence_count": len([s for s in content.split('.') if s.strip()]),
            "paragraph_count": len([p for p in content.split('\n\n') if p.strip()]),
            "has_dialogue": '"' in content or '—' in content,
            "dialogue_ratio": content.count('"') / max(len(content), 1),
            "has_action_verbs": False,
            "has_descriptions": False,
            "avg_sentence_length": 0,
            "readability": "unknown"
        }
        
        # Calcular longitud promedio de oración
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        if sentences:
            avg_words = sum(len(s.split()) for s in sentences) / len(sentences)
            analysis["avg_sentence_length"] = round(avg_words, 1)
        
        # Detectar verbos de acción
        action_verbs = [
            'corrió', 'saltó', 'golpeó', 'gritó', 'lanzó', 'disparó',
            'esquivó', 'atacó', 'huyó', 'persiguió', 'alcanzó'
        ]
        analysis["has_action_verbs"] = any(verb in content.lower() for verb in action_verbs)
        
        # Detectar descripciones
        descriptive_words = [
            'oscuro', 'brillante', 'enorme', 'pequeño', 'hermoso', 'terrible',
            'frío', 'caliente', 'suave', 'áspero'
        ]
        analysis["has_descriptions"] = any(word in content.lower() for word in descriptive_words)
        
        # Evaluar legibilidad básica
        if analysis["avg_sentence_length"] < 10:
            analysis["readability"] = "muy_simple"
        elif analysis["avg_sentence_length"] < 20:
            analysis["readability"] = "clara"
        elif analysis["avg_sentence_length"] < 30:
            analysis["readability"] = "moderada"
        else:
            analysis["readability"] = "compleja"
        
        return analysis
    
    @staticmethod
    def detect_common_issues(content: str) -> List[str]:
        """
        Detecta problemas comunes en el contenido.
        
        Args:
            content: Contenido a analizar
            
        Returns:
            Lista de problemas detectados
        """
        
        issues = []
        
        # Verificar uso excesivo de adverbios en -mente
        mente_count = len(re.findall(r'\b\w+mente\b', content, re.IGNORECASE))
        if mente_count > 5:
            issues.append(f"Uso excesivo de adverbios terminados en -mente ({mente_count})")
        
        # Verificar repetición de palabras
        words = content.lower().split()
        if len(words) > 50:
            from collections import Counter
            word_freq = Counter(words)
            # Palabras comunes a ignorar
            common_words = {'el', 'la', 'los', 'las', 'de', 'del', 'a', 'en', 'y', 'que', 'se', 'con', 'por', 'para', 'un', 'una'}
            for word, count in word_freq.most_common(10):
                if word not in common_words and len(word) > 4 and count > 5:
                    issues.append(f"Palabra '{word}' repetida {count} veces")
        
        # Verificar uso de clichés
        cliches = [
            'de repente', 'al final del día', 'sin previo aviso',
            'como de costumbre', 'sin decir palabra'
        ]
        content_lower = content.lower()
        for cliche in cliches:
            if cliche in content_lower:
                issues.append(f"Cliché detectado: '{cliche}'")
        
        return issues
    
    # ========================================================================
    # VALIDACIÓN DE BLURB
    # ========================================================================
    
    @staticmethod
    def validate_blurb(blurb: str) -> Tuple[bool, List[str]]:
        """
        Valida un blurb de contraportada.
        
        Args:
            blurb: Texto del blurb
            
        Returns:
            Tupla (válido: bool, lista de problemas: List[str])
        """
        
        problems = []
        
        if not blurb or not blurb.strip():
            problems.append("Blurb vacío")
            return False, problems
        
        word_count = len(blurb.split())
        
        if word_count < 100:
            problems.append(f"Blurb demasiado corto: {word_count} palabras (mínimo 100)")
        
        if word_count > 250:
            problems.append(f"Blurb demasiado largo: {word_count} palabras (máximo 250)")
        
        # Verificar que no tenga spoilers obvios
        spoiler_words = ['al final', 'finalmente', 'descubre que', 'resulta ser']
        for word in spoiler_words:
            if word in blurb.lower():
                problems.append(f"Posible spoiler detectado: '{word}'")
        
        is_valid = len(problems) == 0
        
        return is_valid, problems