"""
Actualizador de estados de personajes.
Analiza capítulos completados y actualiza el estado de los personajes.
"""

import json
import re
from typing import Dict, Any, List, Callable, Optional
from ..prompts.templates import PromptTemplates


class CharacterUpdater:
    """
    Actualizador especializado para mantener el estado de los personajes.
    Analiza contenido generado y extrae cambios relevantes.
    """
    
    def __init__(self, api_caller: Callable[[str], str]):
        """
        Inicializa el actualizador de personajes.
        
        Args:
            api_caller: Función para llamar a la API de LLM
        """
        self.api_caller = api_caller
    
    # ========================================================================
    # ACTUALIZACIÓN PRINCIPAL
    # ========================================================================
    
    def update_after_chapter(self,
                            chapter_content: str,
                            character_names: List[str],
                            current_states: Dict[str, str]) -> Dict[str, str]:
        """
        Actualiza el estado de los personajes después de completar un capítulo.
        
        Args:
            chapter_content: Contenido completo del capítulo
            character_names: Lista de nombres de personajes a actualizar
            current_states: Estados actuales de los personajes
            
        Returns:
            Diccionario con estados actualizados {nombre: nuevo_estado}
        """
        
        if not character_names:
            return {}
        
        # Construir prompt usando template
        prompt = PromptTemplates.character_update(
            chapter_content=chapter_content,
            character_names=character_names
        )
        
        # Llamar a la API
        response = self.api_caller(prompt)
        
        # Parsear respuesta
        updates = self._parse_update_response(response)
        
        if not updates:
            # Si falla, mantener estados actuales
            print("⚠️ No se pudieron actualizar estados de personajes automáticamente")
            return current_states
        
        # Validar y limpiar actualizaciones
        updates = self._validate_updates(updates, character_names, current_states)
        
        return updates
    
    # ========================================================================
    # PARSING Y VALIDACIÓN
    # ========================================================================
    
    def _parse_update_response(self, response: str) -> Optional[Dict[str, str]]:
        """
        Parsea la respuesta del modelo.
        
        Args:
            response: Respuesta cruda del modelo
            
        Returns:
            Diccionario con actualizaciones o None si falla
        """
        try:
            # Limpiar respuesta
            cleaned = response.strip()
            cleaned = re.sub(r'^```json\s*', '', cleaned)
            cleaned = re.sub(r'^```\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)
            cleaned = cleaned.strip()
            
            # Parsear JSON
            data = json.loads(cleaned)
            
            # Extraer character_updates
            if 'character_updates' in data:
                return data['character_updates']
            else:
                return data
            
        except json.JSONDecodeError as e:
            print(f"❌ Error al parsear actualización de personajes: {e}")
            return None
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            return None
    
    def _validate_updates(self,
                         updates: Dict[str, str],
                         expected_names: List[str],
                         current_states: Dict[str, str]) -> Dict[str, str]:
        """
        Valida y limpia las actualizaciones.
        
        Args:
            updates: Actualizaciones propuestas
            expected_names: Nombres de personajes esperados
            current_states: Estados actuales
            
        Returns:
            Actualizaciones validadas
        """
        
        validated = {}
        
        for name in expected_names:
            if name in updates:
                new_state = updates[name].strip()
                
                # Validar que no esté vacío
                if new_state and len(new_state) > 5:
                    # Limitar longitud
                    if len(new_state) > 200:
                        new_state = new_state[:197] + "..."
                    
                    validated[name] = new_state
                    print(f"📝 Estado de '{name}' actualizado")
                else:
                    # Mantener estado actual
                    validated[name] = current_states.get(name, "Estado desconocido")
            else:
                # Personaje no mencionado, mantener estado
                validated[name] = current_states.get(name, "Estado desconocido")
        
        return validated
    
    # ========================================================================
    # ANÁLISIS DE PERSONAJES
    # ========================================================================
    
    def extract_character_mentions(self, text: str, character_names: List[str]) -> Dict[str, int]:
        """
        Cuenta cuántas veces aparece cada personaje en el texto.
        
        Args:
            text: Texto a analizar
            character_names: Lista de nombres de personajes
            
        Returns:
            Diccionario con conteos {nombre: menciones}
        """
        
        mentions = {}
        
        for name in character_names:
            # Buscar nombre completo y posibles variaciones (primer nombre)
            full_name_count = text.count(name)
            
            # Intentar con primer nombre si es nombre compuesto
            first_name = name.split()[0] if ' ' in name else name
            first_name_count = text.count(first_name) if first_name != name else 0
            
            total = full_name_count + first_name_count
            mentions[name] = total
        
        return mentions
    
    def identify_active_characters(self,
                                  text: str,
                                  all_characters: List[str],
                                  threshold: int = 2) -> List[str]:
        """
        Identifica qué personajes son activos en un texto.
        
        Args:
            text: Texto a analizar
            all_characters: Lista de todos los personajes
            threshold: Número mínimo de menciones para considerar activo
            
        Returns:
            Lista de personajes activos
        """
        
        mentions = self.extract_character_mentions(text, all_characters)
        
        active = [
            name for name, count in mentions.items()
            if count >= threshold
        ]
        
        return active
    
    # ========================================================================
    # ANÁLISIS DE CAMBIOS
    # ========================================================================
    
    def detect_significant_changes(self,
                                   old_state: str,
                                   new_state: str) -> Dict[str, Any]:
        """
        Detecta si hubo cambios significativos en el estado.
        
        Args:
            old_state: Estado anterior
            new_state: Estado nuevo
            
        Returns:
            Análisis de cambios
        """
        
        # Palabras clave de cambio emocional
        emotional_keywords = [
            'feliz', 'triste', 'enojado', 'asustado', 'confundido',
            'determinado', 'desesperado', 'esperanzado', 'resignado'
        ]
        
        # Palabras clave de cambio físico
        physical_keywords = [
            'herido', 'cansado', 'recuperado', 'débil', 'fuerte',
            'enfermo', 'sano'
        ]
        
        old_lower = old_state.lower()
        new_lower = new_state.lower()
        
        emotional_change = any(kw in new_lower and kw not in old_lower for kw in emotional_keywords)
        physical_change = any(kw in new_lower and kw not in old_lower for kw in physical_keywords)
        
        return {
            "has_emotional_change": emotional_change,
            "has_physical_change": physical_change,
            "has_any_change": emotional_change or physical_change,
            "state_length_change": len(new_state) - len(old_state)
        }
    
    # ========================================================================
    # UTILIDADES
    # ========================================================================
    
    def format_character_summary(self, 
                                characters: Dict[str, Dict[str, Any]]) -> str:
        """
        Formatea un resumen legible de los personajes.
        
        Args:
            characters: Diccionario de personajes con sus datos
            
        Returns:
            String formateado con resumen
        """
        
        summary = "👥 PERSONAJES DEL LIBRO\n"
        summary += "=" * 60 + "\n\n"
        
        for name, data in characters.items():
            summary += f"**{name}**\n"
            summary += f"   Estado actual: {data.get('current_state', 'Desconocido')}\n"
            
            if 'description' in data:
                desc = data['description'][:100]
                summary += f"   Descripción: {desc}...\n"
            
            summary += "\n"
        
        return summary
    
    def get_character_arc_summary(self,
                                 character_name: str,
                                 state_history: List[str]) -> str:
        """
        Genera un resumen del arco del personaje.
        
        Args:
            character_name: Nombre del personaje
            state_history: Lista cronológica de estados
            
        Returns:
            Resumen del arco
        """
        
        if not state_history:
            return f"{character_name}: Sin historia registrada"
        
        summary = f"📖 ARCO DE {character_name}\n"
        summary += "-" * 40 + "\n"
        
        for i, state in enumerate(state_history, 1):
            summary += f"{i}. {state}\n"
        
        return summary