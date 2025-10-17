"""
Gestor de estilos de escritura. Coordina la configuración del perfil
y proporciona acceso a las instrucciones adaptadas.
"""

from typing import Dict, Any, Optional, List
from .style_profiles import (
    STYLE_PRESETS, 
    DEFAULT_PROFILE, 
    WRITING_DIMENSIONS,
    get_profile_info,
    get_dimension_info
)
import copy


class StyleManager:
    """
    Gestiona la configuración de estilo del libro.
    Permite usar perfiles predefinidos o configuraciones personalizadas.
    """
    
    def __init__(self, 
                 profile_name: str = DEFAULT_PROFILE,
                 custom_dimensions: Optional[Dict[str, str]] = None,
                 custom_instructions: Optional[List[str]] = None):
        """
        Inicializa el gestor de estilos.
        
        Args:
            profile_name: Nombre del perfil predefinido a usar
            custom_dimensions: Sobrescribir dimensiones específicas
            custom_instructions: Instrucciones adicionales personalizadas
        """
        self.profile_name = profile_name
        self.profile_config = self._load_profile(profile_name)
        
        # Aplicar personalizaciones si existen
        if custom_dimensions:
            self._apply_custom_dimensions(custom_dimensions)
        
        if custom_instructions:
            self._add_custom_instructions(custom_instructions)
    
    # ========================================================================
    # CARGA Y CONFIGURACIÓN
    # ========================================================================
    
    def _load_profile(self, profile_name: str) -> Dict[str, Any]:
        """
        Carga un perfil de estilo.
        
        Args:
            profile_name: Nombre del perfil
            
        Returns:
            Configuración del perfil (copia profunda)
        """
        profile_info = get_profile_info(profile_name)
        
        # Hacer una copia profunda para no modificar el original
        return copy.deepcopy(profile_info)
    
    def _apply_custom_dimensions(self, custom_dimensions: Dict[str, str]):
        """
        Aplica dimensiones personalizadas sobre el perfil base.
        
        Args:
            custom_dimensions: Dict con dimensiones a sobrescribir
        """
        current_dimensions = self.profile_config.get('dimensions', {})
        
        for dimension, level in custom_dimensions.items():
            # Validar que la dimensión exista
            if dimension in WRITING_DIMENSIONS:
                # Validar que el nivel exista en esa dimensión
                if level in WRITING_DIMENSIONS[dimension]:
                    current_dimensions[dimension] = level
                else:
                    print(f"⚠️ Advertencia: Nivel '{level}' no válido para dimensión '{dimension}'")
            else:
                print(f"⚠️ Advertencia: Dimensión '{dimension}' no reconocida")
        
        self.profile_config['dimensions'] = current_dimensions
    
    def _add_custom_instructions(self, custom_instructions: List[str]):
        """
        Agrega instrucciones personalizadas al perfil.
        
        Args:
            custom_instructions: Lista de instrucciones adicionales
        """
        current_instructions = self.profile_config.get('special_instructions', [])
        current_instructions.extend(custom_instructions)
        self.profile_config['special_instructions'] = current_instructions
    
    # ========================================================================
    # ACCESO A CONFIGURACIÓN
    # ========================================================================
    
    def get_full_config(self) -> Dict[str, Any]:
        """
        Retorna la configuración completa del estilo.
        
        Returns:
            Diccionario con toda la configuración
        """
        return copy.deepcopy(self.profile_config)
    
    def get_dimension(self, dimension_name: str) -> str:
        """
        Obtiene el nivel configurado para una dimensión.
        
        Args:
            dimension_name: Nombre de la dimensión
            
        Returns:
            Nivel configurado (ej: 'complex', 'fast_paced', etc)
        """
        return self.profile_config.get('dimensions', {}).get(dimension_name, 'moderate')
    
    def get_dimension_details(self, dimension_name: str) -> Dict[str, Any]:
        """
        Obtiene información detallada de la dimensión configurada.
        
        Args:
            dimension_name: Nombre de la dimensión
            
        Returns:
            Diccionario con información completa de la dimensión
        """
        level = self.get_dimension(dimension_name)
        return get_dimension_info(dimension_name, level)
    
    def get_special_instructions(self) -> List[str]:
        """
        Retorna las instrucciones especiales del perfil.
        
        Returns:
            Lista de instrucciones
        """
        return self.profile_config.get('special_instructions', [])
    
    def get_avoid_list(self) -> List[str]:
        """
        Retorna la lista de elementos a evitar.
        
        Returns:
            Lista de elementos a evitar
        """
        return self.profile_config.get('avoid', [])
    
    # ========================================================================
    # INFORMACIÓN Y DIAGNÓSTICO
    # ========================================================================
    
    def get_summary(self) -> str:
        """
        Genera un resumen legible del perfil configurado.
        
        Returns:
            String con resumen formateado
        """
        config = self.profile_config
        
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║  PERFIL DE ESTILO: {config.get('name', 'Sin nombre')[:43].ljust(43)} ║
╚══════════════════════════════════════════════════════════════╝

📝 Descripción:
   {config.get('description', 'Sin descripción')}

📊 Dimensiones Configuradas:
"""
        
        dimensions = config.get('dimensions', {})
        for dim_key, level in dimensions.items():
            dim_info = get_dimension_info(dim_key, level)
            dim_name = dim_key.replace('_', ' ').title()
            level_name = dim_info.get('name', level) if dim_info else level
            summary += f"   • {dim_name}: {level_name}\n"
        
        special = self.get_special_instructions()
        if special:
            summary += f"\n✨ Instrucciones Especiales: {len(special)} configuradas\n"
        
        avoid = self.get_avoid_list()
        if avoid:
            summary += f"⚠️  Elementos a Evitar: {len(avoid)} configurados\n"
        
        return summary
    
    def is_complex_narrative(self) -> bool:
        """
        Determina si el perfil requiere narrativa compleja.
        
        Returns:
            True si requiere complejidad narrativa alta
        """
        prose = self.get_dimension('prose_complexity')
        thematic = self.get_dimension('thematic_depth')
        
        return prose in ['complex', 'experimental'] or thematic in ['philosophical', 'deconstructive']
    
    def is_fast_paced(self) -> bool:
        """
        Determina si el perfil requiere ritmo rápido.
        
        Returns:
            True si el ritmo debe ser rápido
        """
        narrative = self.get_dimension('narrative_density')
        return narrative == 'fast_paced'
    
    def requires_rich_descriptions(self) -> bool:
        """
        Determina si el perfil requiere descripciones ricas.
        
        Returns:
            True si las descripciones deben ser detalladas
        """
        description = self.get_dimension('description_level')
        return description in ['rich', 'immersive']
    
    # ========================================================================
    # MODIFICACIÓN DINÁMICA
    # ========================================================================
    
    def update_dimension(self, dimension_name: str, new_level: str):
        """
        Actualiza una dimensión específica del perfil.
        
        Args:
            dimension_name: Nombre de la dimensión a actualizar
            new_level: Nuevo nivel para la dimensión
        """
        if dimension_name not in WRITING_DIMENSIONS:
            raise ValueError(f"Dimensión '{dimension_name}' no reconocida")
        
        if new_level not in WRITING_DIMENSIONS[dimension_name]:
            raise ValueError(f"Nivel '{new_level}' no válido para dimensión '{dimension_name}'")
        
        self.profile_config['dimensions'][dimension_name] = new_level
        print(f"✅ Dimensión '{dimension_name}' actualizada a '{new_level}'")
    
    def add_instruction(self, instruction: str):
        """
        Agrega una nueva instrucción especial.
        
        Args:
            instruction: Instrucción a agregar
        """
        instructions = self.profile_config.get('special_instructions', [])
        instructions.append(instruction)
        self.profile_config['special_instructions'] = instructions
        print(f"✅ Instrucción agregada")
    
    def add_avoid_item(self, item: str):
        """
        Agrega un elemento a la lista de cosas a evitar.
        
        Args:
            item: Elemento a evitar
        """
        avoid_list = self.profile_config.get('avoid', [])
        avoid_list.append(item)
        self.profile_config['avoid'] = avoid_list
        print(f"✅ Elemento agregado a la lista de evitar")
    
    # ========================================================================
    # EXPORTACIÓN
    # ========================================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Exporta la configuración completa como diccionario.
        
        Returns:
            Diccionario con toda la configuración
        """
        return {
            'profile_name': self.profile_name,
            'config': copy.deepcopy(self.profile_config)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StyleManager':
        """
        Crea un StyleManager desde un diccionario exportado.
        
        Args:
            data: Diccionario con configuración exportada
            
        Returns:
            Nueva instancia de StyleManager
        """
        manager = cls(profile_name=data.get('profile_name', DEFAULT_PROFILE))
        manager.profile_config = copy.deepcopy(data.get('config', {}))
        return manager