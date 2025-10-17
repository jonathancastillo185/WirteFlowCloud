"""
Generador de outlines para libros.
Maneja la creación de la estructura completa de la novela.
"""

import json
import re
from typing import Dict, Any, Callable, Optional
from ..prompts.templates import PromptTemplates
from ..styles.prompt_builder import PromptBuilder


class OutlineGenerator:
    """
    Generador especializado para crear outlines de libros.
    Coordina con el sistema de estilos para adaptar la estructura.
    """
    
    def __init__(self, 
                 api_caller: Callable[[str], str],
                 prompt_builder: PromptBuilder):
        """
        Inicializa el generador de outlines.
        
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
                premise: str,
                num_chapters: int,
                themes: str,
                author_style: str) -> Dict[str, Any]:
        """
        Genera el outline completo del libro.
        
        Args:
            premise: Premisa de la historia
            num_chapters: Número de capítulos
            themes: Temas a explorar (string separado por comas)
            author_style: Estilo del autor
            
        Returns:
            Diccionario con el outline completo o error
        """
        
        # Construir el prompt usando el sistema de estilos
        prompt = self.prompt_builder.build_outline_prompt(
            premise=premise,
            num_chapters=num_chapters,
            themes=themes,
            author_style=author_style
        )
        
        # Llamar a la API
        response = self.api_caller(prompt)
        
        # Parsear y validar la respuesta
        outline_data = self._parse_outline_response(response)
        
        if outline_data is None:
            return {
                "error": True,
                "message": PromptTemplates.error_json_parse(response)
            }
        
        # Validar estructura del outline
        validation_result = self._validate_outline(outline_data, num_chapters)
        
        if not validation_result["valid"]:
            return {
                "error": True,
                "message": f"❌ Outline generado con estructura inválida: {validation_result['message']}"
            }
        
        # Post-procesar el outline
        outline_data = self._post_process_outline(outline_data, num_chapters)
        
        return {
            "error": False,
            "data": outline_data,
            "message": "✅ Outline, mundo y personajes generados con éxito."
        }
    
    # ========================================================================
    # PARSING Y VALIDACIÓN
    # ========================================================================
    
    def _parse_outline_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Parsea la respuesta del modelo como JSON.
        
        Args:
            response: Respuesta cruda del modelo
            
        Returns:
            Diccionario parseado o None si falla
        """
        try:
            # Limpiar la respuesta de posibles bloques markdown
            cleaned = response.strip()
            cleaned = re.sub(r'^```json\s*', '', cleaned)
            cleaned = re.sub(r'^```\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)
            cleaned = cleaned.strip()
            
            # Parsear JSON
            data = json.loads(cleaned)
            return data
            
        except json.JSONDecodeError as e:
            print(f"❌ Error al parsear JSON: {e}")
            print(f"Posición del error: {e.pos}")
            print(f"Línea: {e.lineno}, Columna: {e.colno}")
            return None
        except Exception as e:
            print(f"❌ Error inesperado al parsear: {e}")
            return None
    
    def _validate_outline(self, data: Dict[str, Any], expected_chapters: int) -> Dict[str, Any]:
        """
        Valida que el outline tenga la estructura correcta.
        
        Args:
            data: Datos del outline parseado
            expected_chapters: Número esperado de capítulos
            
        Returns:
            Dict con 'valid' (bool) y 'message' (str)
        """
        
        # Verificar secciones principales
        required_sections = ['world', 'characters', 'plot', 'style', 'consistency_rules']
        
        for section in required_sections:
            if section not in data:
                return {
                    "valid": False,
                    "message": f"Falta la sección requerida: '{section}'"
                }
        
        # Validar world
        if not isinstance(data['world'], dict):
            return {"valid": False, "message": "'world' debe ser un diccionario"}
        
        required_world_keys = ['setting', 'time_period']
        for key in required_world_keys:
            if key not in data['world']:
                return {"valid": False, "message": f"'world' debe contener '{key}'"}
        
        # Validar characters
        if not isinstance(data['characters'], dict):
            return {"valid": False, "message": "'characters' debe ser un diccionario"}
        
        if len(data['characters']) == 0:
            return {"valid": False, "message": "Debe haber al menos un personaje"}
        
        # Validar plot
        if 'outline' not in data['plot']:
            return {"valid": False, "message": "'plot' debe contener 'outline'"}
        
        if not isinstance(data['plot']['outline'], list):
            return {"valid": False, "message": "'plot.outline' debe ser una lista"}
        
        outline = data['plot']['outline']
        
        if len(outline) != expected_chapters:
            return {
                "valid": False, 
                "message": f"Se esperaban {expected_chapters} capítulos, se recibieron {len(outline)}"
            }
        
        # Validar cada capítulo
        required_chapter_keys = ['number', 'title', 'summary', 'key_events', 'pages_estimate']
        
        for i, chapter in enumerate(outline):
            if not isinstance(chapter, dict):
                return {"valid": False, "message": f"Capítulo {i+1} debe ser un diccionario"}
            
            for key in required_chapter_keys:
                if key not in chapter:
                    return {
                        "valid": False,
                        "message": f"Capítulo {i+1} debe contener '{key}'"
                    }
            
            # Validar número de capítulo
            if chapter['number'] != i + 1:
                return {
                    "valid": False,
                    "message": f"Capítulo {i+1} tiene número incorrecto: {chapter['number']}"
                }
            
            # Validar key_events
            if not isinstance(chapter['key_events'], list) or len(chapter['key_events']) == 0:
                return {
                    "valid": False,
                    "message": f"Capítulo {i+1} debe tener al menos un key_event"
                }
        
        return {"valid": True, "message": "Outline válido"}
    
    def _post_process_outline(self, data: Dict[str, Any], num_chapters: int) -> Dict[str, Any]:
        """
        Post-procesa el outline para asegurar consistencia.
        
        Args:
            data: Datos del outline
            num_chapters: Número de capítulos
            
        Returns:
            Outline procesado
        """
        
        # Asegurar que cada personaje tiene un estado inicial
        for char_name, char_data in data['characters'].items():
            if 'current_state' not in char_data:
                char_data['current_state'] = "Al inicio de la historia."
        
        # Normalizar páginas estimadas
        for chapter in data['plot']['outline']:
            if 'pages_estimate' not in chapter or chapter['pages_estimate'] <= 0:
                chapter['pages_estimate'] = 12  # Default
        
        # Asegurar que hay character_focus
        for chapter in data['plot']['outline']:
            if 'character_focus' not in chapter:
                chapter['character_focus'] = []
        
        # Asegurar consistencia en plot
        if 'premise' not in data['plot']:
            data['plot']['premise'] = ""
        
        if 'themes' not in data['plot']:
            data['plot']['themes'] = []
        
        return data
    
    # ========================================================================
    # UTILIDADES
    # ========================================================================
    
    def get_outline_summary(self, outline_data: Dict[str, Any]) -> str:
        """
        Genera un resumen legible del outline generado.
        
        Args:
            outline_data: Datos del outline
            
        Returns:
            String con resumen formateado
        """
        
        summary = "📚 OUTLINE GENERADO\n"
        summary += "=" * 60 + "\n\n"
        
        # Mundo
        world = outline_data.get('world', {})
        summary += f"🌍 MUNDO:\n"
        summary += f"   Setting: {world.get('setting', 'N/A')}\n"
        summary += f"   Período: {world.get('time_period', 'N/A')}\n"
        
        locations = world.get('key_locations', {})
        if locations:
            summary += f"   Ubicaciones: {len(locations)} definidas\n"
        
        summary += "\n"
        
        # Personajes
        characters = outline_data.get('characters', {})
        summary += f"👥 PERSONAJES: {len(characters)} principales\n"
        for name in list(characters.keys())[:5]:  # Mostrar solo primeros 5
            summary += f"   - {name}\n"
        if len(characters) > 5:
            summary += f"   ... y {len(characters) - 5} más\n"
        
        summary += "\n"
        
        # Capítulos
        outline = outline_data.get('plot', {}).get('outline', [])
        summary += f"📖 ESTRUCTURA: {len(outline)} capítulos\n"
        
        total_pages = sum(ch.get('pages_estimate', 0) for ch in outline)
        summary += f"📄 Páginas estimadas: {total_pages}\n"
        
        summary += "\n"
        
        # Primeros 3 capítulos
        summary += "PRIMEROS CAPÍTULOS:\n"
        for chapter in outline[:3]:
            summary += f"   {chapter['number']}. {chapter['title']}\n"
            summary += f"      {chapter.get('summary', 'Sin resumen')[:80]}...\n"
        
        if len(outline) > 3:
            summary += f"   ... y {len(outline) - 3} capítulos más\n"
        
        return summary