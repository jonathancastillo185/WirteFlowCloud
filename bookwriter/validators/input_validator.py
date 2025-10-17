"""
Validador de entradas del usuario.
Asegura que los datos proporcionados sean válidos antes de procesarlos.
"""

import re
from typing import Dict, Any, List, Tuple
from pathlib import Path


class InputValidator:
    """
    Valida todas las entradas del usuario antes de procesamiento.
    Retorna mensajes de error claros y específicos.
    """
    
    # ========================================================================
    # VALIDACIÓN DE PROYECTO
    # ========================================================================
    
    @staticmethod
    def validate_project_name(name: str) -> Tuple[bool, str]:
        """
        Valida el nombre del proyecto.
        
        Args:
            name: Nombre propuesto para el proyecto
            
        Returns:
            Tupla (válido: bool, mensaje: str)
        """
        
        if not name or not name.strip():
            return False, "❌ El nombre del proyecto no puede estar vacío"
        
        name = name.strip()
        
        # Longitud
        if len(name) < 3:
            return False, "❌ El nombre debe tener al menos 3 caracteres"
        
        if len(name) > 100:
            return False, "❌ El nombre es demasiado largo (máximo 100 caracteres)"
        
        # Caracteres permitidos (más flexible para soportar acentos)
        # Solo rechazamos caracteres claramente problemáticos
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            if char in name:
                return False, f"❌ El nombre contiene caracteres no permitidos: {char}"
        
        return True, "✅ Nombre válido"
    
    @staticmethod
    def validate_project_creation(name: str,
                                  premise: str,
                                  chapters: int,
                                  themes: str,
                                  authors: List[str]) -> Tuple[bool, str]:
        """
        Valida todos los parámetros de creación de proyecto.
        
        Args:
            name: Nombre del proyecto
            premise: Premisa de la historia
            chapters: Número de capítulos
            themes: Temas (string separado por comas)
            authors: Lista de autores seleccionados
            
        Returns:
            Tupla (válido: bool, mensaje: str)
        """
        
        # Validar nombre
        valid, msg = InputValidator.validate_project_name(name)
        if not valid:
            return False, msg
        
        # Validar premisa
        valid, msg = InputValidator.validate_premise(premise)
        if not valid:
            return False, msg
        
        # Validar número de capítulos
        valid, msg = InputValidator.validate_chapter_count(chapters)
        if not valid:
            return False, msg
        
        # Validar temas
        valid, msg = InputValidator.validate_themes(themes)
        if not valid:
            return False, msg
        
        # Validar autores
        valid, msg = InputValidator.validate_author_selection(authors)
        if not valid:
            return False, msg
        
        return True, "✅ Todos los parámetros son válidos"
    
    # ========================================================================
    # VALIDACIÓN DE PARÁMETROS INDIVIDUALES
    # ========================================================================
    
    @staticmethod
    def validate_premise(premise: str) -> Tuple[bool, str]:
        """
        Valida la premisa de la historia.
        
        Args:
            premise: Premisa propuesta
            
        Returns:
            Tupla (válido: bool, mensaje: str)
        """
        
        if not premise or not premise.strip():
            return False, "❌ La premisa no puede estar vacía"
        
        premise = premise.strip()
        
        # Longitud mínima
        if len(premise) < 20:
            return False, "❌ La premisa es demasiado corta (mínimo 20 caracteres). Proporciona más detalles sobre la historia."
        
        # Longitud máxima
        if len(premise) > 2000:
            return False, "❌ La premisa es demasiado larga (máximo 2000 caracteres). Intenta ser más conciso."
        
        # Verificar que tenga al menos algunas palabras
        word_count = len(premise.split())
        if word_count < 10:
            return False, "❌ La premisa debe tener al menos 10 palabras. Describe mejor tu idea."
        
        return True, "✅ Premisa válida"
    
    @staticmethod
    def validate_chapter_count(chapters: int) -> Tuple[bool, str]:
        """
        Valida el número de capítulos.
        
        Args:
            chapters: Número de capítulos
            
        Returns:
            Tupla (válido: bool, mensaje: str)
        """
        
        if not isinstance(chapters, int):
            try:
                chapters = int(chapters)
            except (ValueError, TypeError):
                return False, "❌ El número de capítulos debe ser un número entero"
        
        if chapters < 3:
            return False, "❌ El libro debe tener al menos 3 capítulos"
        
        if chapters > 50:
            return False, "❌ El número máximo de capítulos es 50. Para libros más largos, considera dividir en volúmenes."
        
        return True, f"✅ {chapters} capítulos es válido"
    
    @staticmethod
    def validate_themes(themes: str) -> Tuple[bool, str]:
        """
        Valida los temas proporcionados.
        
        Args:
            themes: Temas separados por comas
            
        Returns:
            Tupla (válido: bool, mensaje: str)
        """
        
        if not themes or not themes.strip():
            return False, "❌ Debes especificar al menos un tema para la historia"
        
        themes = themes.strip()
        
        # Separar y limpiar temas
        theme_list = [t.strip() for t in themes.split(',') if t.strip()]
        
        if len(theme_list) == 0:
            return False, "❌ Debes especificar al menos un tema válido"
        
        if len(theme_list) > 10:
            return False, "❌ Demasiados temas (máximo 10). Enfócate en los más importantes."
        
        # Validar longitud de cada tema
        for theme in theme_list:
            if len(theme) < 3:
                return False, f"❌ El tema '{theme}' es demasiado corto (mínimo 3 caracteres)"
            if len(theme) > 50:
                return False, f"❌ El tema '{theme}' es demasiado largo (máximo 50 caracteres)"
        
        return True, f"✅ {len(theme_list)} tema(s) válido(s)"
    
    @staticmethod
    def validate_author_selection(authors: List[str]) -> Tuple[bool, str]:
        """
        Valida la selección de autores.
        
        Args:
            authors: Lista de autores seleccionados
            
        Returns:
            Tupla (válido: bool, mensaje: str)
        """
        
        if not authors or len(authors) == 0:
            return False, "❌ Debes seleccionar al menos un autor como referencia de estilo"
        
        if len(authors) > 5:
            return False, "❌ Demasiados autores seleccionados (máximo 5). Elegir muchos estilos puede diluir la coherencia."
        
        # Validar que no haya strings vacíos
        authors = [a for a in authors if a and a.strip()]
        
        if len(authors) == 0:
            return False, "❌ Selección de autores inválida"
        
        return True, f"✅ {len(authors)} autor(es) seleccionado(s)"
    
    # ========================================================================
    # VALIDACIÓN DE RUTAS Y ARCHIVOS
    # ========================================================================
    
    @staticmethod
    def validate_project_path(project_path: Path) -> Tuple[bool, str]:
        """
        Valida que la ruta del proyecto sea válida y accesible.
        
        Args:
            project_path: Ruta del proyecto
            
        Returns:
            Tupla (válido: bool, mensaje: str)
        """
        
        try:
            # Verificar que el path sea válido
            if not project_path.exists():
                return True, "✅ Ruta válida (proyecto nuevo)"
            
            # Si existe, verificar que sea un directorio
            if not project_path.is_dir():
                return False, "❌ La ruta existe pero no es un directorio"
            
            # Verificar permisos de escritura
            test_file = project_path / '.write_test'
            try:
                test_file.touch()
                test_file.unlink()
                return True, "✅ Ruta válida y con permisos de escritura"
            except PermissionError:
                return False, "❌ No hay permisos de escritura en esta ruta"
            
        except Exception as e:
            return False, f"❌ Error al validar ruta: {str(e)}"
    
    @staticmethod
    def validate_file_exists(file_path: Path, file_description: str) -> Tuple[bool, str]:
        """
        Valida que un archivo exista.
        
        Args:
            file_path: Ruta del archivo
            file_description: Descripción del archivo para el mensaje
            
        Returns:
            Tupla (válido: bool, mensaje: str)
        """
        
        if not file_path.exists():
            return False, f"❌ {file_description} no existe: {file_path.name}"
        
        if not file_path.is_file():
            return False, f"❌ {file_description} no es un archivo válido"
        
        return True, f"✅ {file_description} encontrado"
    
    # ========================================================================
    # VALIDACIÓN DE CONFIGURACIÓN
    # ========================================================================
    
    @staticmethod
    def validate_style_profile(profile_name: str, 
                              available_profiles: List[str]) -> Tuple[bool, str]:
        """
        Valida que el perfil de estilo exista.
        
        Args:
            profile_name: Nombre del perfil
            available_profiles: Lista de perfiles disponibles
            
        Returns:
            Tupla (válido: bool, mensaje: str)
        """
        
        if not profile_name or not profile_name.strip():
            return False, "❌ Debes seleccionar un perfil de estilo"
        
        if profile_name not in available_profiles:
            return False, f"❌ Perfil '{profile_name}' no existe. Perfiles disponibles: {', '.join(available_profiles)}"
        
        return True, f"✅ Perfil '{profile_name}' válido"
    
    @staticmethod
    def validate_custom_dimensions(dimensions: Dict[str, str],
                                   valid_dimensions: Dict[str, List[str]]) -> Tuple[bool, str]:
        """
        Valida dimensiones personalizadas.
        
        Args:
            dimensions: Dimensiones a validar
            valid_dimensions: Diccionario de dimensiones válidas
            
        Returns:
            Tupla (válido: bool, mensaje: str)
        """
        
        for dimension, level in dimensions.items():
            if dimension not in valid_dimensions:
                return False, f"❌ Dimensión '{dimension}' no reconocida"
            
            if level not in valid_dimensions[dimension]:
                valid_levels = ', '.join(valid_dimensions[dimension].keys())
                return False, f"❌ Nivel '{level}' no válido para '{dimension}'. Opciones: {valid_levels}"
        
        return True, "✅ Dimensiones personalizadas válidas"
    
    # ========================================================================
    # SANITIZACIÓN
    # ========================================================================
    
    @staticmethod
    def sanitize_project_name(name: str) -> str:
        """
        Sanitiza el nombre del proyecto para uso en sistema de archivos.
        
        Args:
            name: Nombre a sanitizar
            
        Returns:
            Nombre sanitizado
        """
        
        # Eliminar espacios al inicio/final
        name = name.strip()
        
        # Reemplazar caracteres problemáticos
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        
        # Reemplazar múltiples espacios/guiones bajos consecutivos
        name = re.sub(r'[\s_]+', '_', name)
        
        # Limitar longitud
        if len(name) > 100:
            name = name[:100]
        
        return name
    
    @staticmethod
    def sanitize_themes(themes: str) -> List[str]:
        """
        Sanitiza y normaliza los temas.
        
        Args:
            themes: String de temas separados por comas
            
        Returns:
            Lista de temas limpia
        """
        
        # Separar por comas
        theme_list = themes.split(',')
        
        # Limpiar cada tema
        cleaned = []
        for theme in theme_list:
            theme = theme.strip()
            if theme:
                # Capitalizar primera letra
                theme = theme[0].upper() + theme[1:] if len(theme) > 1 else theme.upper()
                cleaned.append(theme)
        
        return cleaned