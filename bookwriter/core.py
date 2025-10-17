"""
Motor principal de BookWriter AI.
Orquesta la generación de libros usando el sistema modular de estilos, prompts y generadores.
"""

import json
import re
import time
import logging
from datetime import datetime
from typing import Dict, Tuple, Generator, Union, List, Optional, Any
from pathlib import Path

# Importar configuraciones
from .config import (
    PROJECTS_PATH, MODEL, groq_client,
    TEMPERATURE, MAX_TOKENS, TOP_P, STOP_SEQUENCES
)

# Importar módulos existentes
from .pdf_exporter import export_book_to_pdf
from .semantic_memory import SemanticMemory
from .image_generator import create_composite_cover

# Importar nuevos módulos
from .styles import StyleManager, PromptBuilder, STYLE_PRESETS
from .generators import OutlineGenerator, PageGenerator, CharacterUpdater
from .validators import InputValidator, ContentValidator, ConsistencyValidator

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BookWriter:
    """
    Motor principal para la generación de libros.
    Orquesta todos los componentes del sistema.
    """
    
    def __init__(self, 
                 project_name: str, 
                 author_style: Union[str, List[str]] = "neutral",
                 style_profile: str = "balanced_neutral",
                 custom_dimensions: Optional[Dict[str, str]] = None):
        """
        Inicializa el escritor de libros.
        
        Args:
            project_name: Nombre del proyecto
            author_style: Estilo(s) de autor como referencia
            style_profile: Perfil de estilo predefinido
            custom_dimensions: Dimensiones personalizadas (opcional)
        """
        
        # Validar y sanitizar nombre del proyecto
        is_valid, message = InputValidator.validate_project_name(project_name)
        if not is_valid:
            raise ValueError(message)
        
        self.project_name = InputValidator.sanitize_project_name(project_name)
        self.project_path = PROJECTS_PATH / self.project_name
        self.project_path.mkdir(exist_ok=True)
        
        logger.info(f"Inicializando proyecto: {self.project_name}")
        
        # Validar ruta del proyecto
        path_valid, path_msg = InputValidator.validate_project_path(self.project_path)
        if not path_valid:
            raise ValueError(path_msg)
        
        # Rutas a los archivos del proyecto
        self.memory_file = self.project_path / 'memory.json'
        self.book_file = self.project_path / 'book.md'
        self.pdf_file = self.project_path / f'{self.project_name}.pdf'
        self.cover_file = self.project_path / 'cover.png'
        
        # Inicializar memoria semántica
        self.semantic_memory = SemanticMemory(self.project_path)
        
        # Convertir autor(es) a string si es necesario
        style_str = ", ".join(author_style) if isinstance(author_style, list) else author_style
        
        # Inicializar memoria del proyecto
        self.memory = self._get_initial_memory(self.project_name, style_str, style_profile)
        self.load_memory()
        
        # Inicializar sistema de estilos
        self.style_manager = StyleManager(
            profile_name=style_profile,
            custom_dimensions=custom_dimensions
        )
        
        # Inicializar constructor de prompts
        self.prompt_builder = PromptBuilder(
            style_config=self.style_manager.get_full_config()
        )
        
        # Inicializar generadores
        self.outline_generator = OutlineGenerator(
            api_caller=self._call_groq,
            prompt_builder=self.prompt_builder
        )
        
        self.page_generator = PageGenerator(
            api_caller=self._call_groq,
            prompt_builder=self.prompt_builder
        )
        
        self.character_updater = CharacterUpdater(
            api_caller=self._call_groq
        )
        
        logger.info(f"✅ Proyecto '{self.project_name}' inicializado con perfil '{style_profile}'")
        logger.info(self.style_manager.get_summary())
    
    # ========================================================================
    # INICIALIZACIÓN Y PERSISTENCIA
    # ========================================================================
    
    def _get_initial_memory(self, project_name: str, author_style: str, style_profile: str) -> Dict:
        """Genera la estructura inicial de memoria."""
        return {
            "metadata": {
                "title": project_name,
                "author_style": author_style,
                "style_profile": style_profile,
                "created": datetime.now().isoformat(),
                "model": MODEL,
                "blurb": "",
                "cover_prompt": ""
            },
            "world": {},
            "characters": {},
            "plot": {
                "outline": [],
                "premise": "",
                "themes": []
            },
            "style": {},
            "chapters_summary": [],
            "consistency_rules": [],
            "writing_progress": {
                "current_chapter_index": 0,
                "current_page_in_chapter": 0
            }
        }
    
    def save_memory(self):
        """Guarda la memoria del proyecto en disco."""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=4)
            logger.debug(f"Memoria guardada: {self.memory_file}")
        except Exception as e:
            logger.error(f"Error al guardar memoria: {e}")
            raise
    
    def load_memory(self):
        """Carga la memoria del proyecto desde disco."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    loaded_memory = json.load(f)
                
                # Asegurar estructura completa
                loaded_memory.setdefault('metadata', {}).setdefault('blurb', "")
                loaded_memory.setdefault('metadata', {}).setdefault('cover_prompt', "")
                loaded_memory.setdefault('metadata', {}).setdefault('style_profile', 'balanced_neutral')
                
                self.memory = loaded_memory
                logger.info(f"Memoria cargada desde: {self.memory_file}")
                
            except json.JSONDecodeError as e:
                logger.error(f"Archivo memory.json corrupto: {e}")
                logger.warning("Usando memoria inicial por defecto")
        else:
            logger.info("No existe memoria previa, usando memoria inicial")
    
    # ========================================================================
    # LLAMADAS A LA API
    # ========================================================================
    
    def _call_groq(self, user_prompt: str) -> str:
        """
        Realiza una llamada a la API de Groq con reintentos y manejo de rate limits.
        
        Args:
            user_prompt: Prompt del usuario
            
        Returns:
            Respuesta del modelo
        """
        max_retries = 5
        
        # Construir prompt del sistema
        system_prompt = self._build_system_prompt()
        
        for attempt in range(max_retries):
            try:
                response = groq_client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS,
                    top_p=TOP_P,
                    stop=STOP_SEQUENCES
                )
                
                content = response.choices[0].message.content
                logger.debug(f"Respuesta recibida: {len(content)} caracteres")
                return content
                
            except Exception as e:
                error_str = str(e)
                
                # Manejar rate limit
                if "429" in error_str and "rate_limit_exceeded" in error_str:
                    wait_match = re.search(r"Please try again in ([\d.]+)s", error_str)
                    if wait_match:
                        wait_seconds = float(wait_match.group(1)) + 1
                        logger.warning(f"Rate limit alcanzado. Esperando {wait_seconds:.2f} segundos...")
                        time.sleep(wait_seconds)
                        continue
                
                logger.error(f"Error en llamada a Groq (intento {attempt + 1}/{max_retries}): {e}")
                
                if attempt + 1 == max_retries:
                    error_msg = f"Error en la llamada a Groq tras {max_retries} intentos: {e}"
                    logger.error(error_msg)
                    return f"Error: {error_msg}"
                
                # Esperar antes de reintentar
                time.sleep(2 ** attempt)  # Backoff exponencial
        
        return f"Error: No se pudo completar la llamada a Groq tras {max_retries} reintentos."
    
    def _build_system_prompt(self) -> str:
        """Construye el prompt del sistema usando el StyleManager."""
        
        metadata = self.memory.get('metadata', {})
        plot_data = self.memory.get('plot', {})
        
        book_metadata = {
            'author_style': metadata.get('author_style', 'neutral'),
            'title': metadata.get('title', 'Sin Título'),
            'premise': plot_data.get('premise', 'No especificada'),
            'themes': plot_data.get('themes', [])
        }
        
        return self.prompt_builder.build_system_prompt(book_metadata)
    
    # ========================================================================
    # GENERACIÓN DE OUTLINE
    # ========================================================================
    
    def generate_outline(self, premise: str, num_chapters: int, themes: str) -> str:
        """
        Genera el outline completo del libro.
        
        Args:
            premise: Premisa de la historia
            num_chapters: Número de capítulos
            themes: Temas separados por comas
            
        Returns:
            Mensaje de resultado
        """
        
        logger.info("=" * 60)
        logger.info("INICIANDO GENERACIÓN DE OUTLINE")
        logger.info("=" * 60)
        
        # Validar entradas
        valid, msg = InputValidator.validate_premise(premise)
        if not valid:
            logger.error(f"Validación fallida: {msg}")
            return msg
        
        valid, msg = InputValidator.validate_chapter_count(num_chapters)
        if not valid:
            logger.error(f"Validación fallida: {msg}")
            return msg
        
        valid, msg = InputValidator.validate_themes(themes)
        if not valid:
            logger.error(f"Validación fallida: {msg}")
            return msg
        
        # Guardar en memoria
        self.memory['plot']['premise'] = premise
        self.memory['plot']['themes'] = InputValidator.sanitize_themes(themes)
        
        # Generar outline usando el generador
        logger.info(f"Generando outline para {num_chapters} capítulos...")
        
        result = self.outline_generator.generate(
            premise=premise,
            num_chapters=num_chapters,
            themes=themes,
            author_style=self.memory['metadata']['author_style']
        )
        
        if result.get('error', False):
            logger.error(f"Error al generar outline: {result['message']}")
            return result['message']
        
        # Actualizar memoria con el outline generado
        outline_data = result['data']
        self.memory.update(outline_data)
        
        # Validar el outline generado
        is_valid, problems = ContentValidator.validate_outline_structure(outline_data)
        
        if not is_valid:
            logger.warning("Outline generado con problemas:")
            for problem in problems:
                logger.warning(f"  - {problem}")
        else:
            logger.info("✅ Outline validado correctamente")
        
        # Inicializar current_state para cada personaje
        for char_name, char_data in self.memory['characters'].items():
            if 'current_state' not in char_data:
                char_data['current_state'] = "Al inicio de la historia."
        
        # Guardar memoria
        self.save_memory()
        
        # Generar resumen del outline
        summary = self.outline_generator.get_outline_summary(outline_data)
        logger.info("\n" + summary)
        
        return result['message']
    
    # ========================================================================
    # GENERACIÓN DE PÁGINAS
    # ========================================================================
    
    def generate_page(self) -> Tuple[str, str]:
        """
        Genera la siguiente página del libro.
        
        Returns:
            Tupla (mensaje_estado, contenido_página)
        """
        
        progress = self.memory.get('writing_progress', {})
        outline = self.memory.get('plot', {}).get('outline', [])
        current_chapter_index = progress.get('current_chapter_index', 0)
        
        # Verificar si el libro está completo
        if not outline or current_chapter_index >= len(outline):
            logger.info("✅ Libro completado")
            return "✅ ¡Libro completado!", ""
        
        chapter_info = outline[current_chapter_index]
        page_in_chapter = progress.get('current_page_in_chapter', 0) + 1
        total_pages = chapter_info.get('pages_estimate', 10)
        
        logger.info(f"Generando página {page_in_chapter}/{total_pages} del capítulo {chapter_info.get('number', 'N/A')}")
        
        # Preparar contexto de personajes
        character_profiles = self._build_character_profiles(chapter_info.get('character_focus', []))
        
        # Obtener último texto escrito
        last_written_text = self._get_last_written_text(1500)
        
        # Obtener contexto de memoria semántica
        query = last_written_text or chapter_info.get('summary', '')
        relevant_context = self.semantic_memory.search_relevant_context(query)
        
        # Detectar tipo de escena (esto podría mejorarse con más contexto)
        scene_type = "mixed"  # Por defecto
        
        # Generar la página
        success, content = self.page_generator.generate(
            chapter_info=chapter_info,
            character_profiles=character_profiles,
            last_written_text=last_written_text,
            relevant_context=relevant_context,
            page_number=page_in_chapter,
            total_pages=total_pages,
            scene_type=scene_type
        )
        
        if not success:
            logger.error(f"Error al generar página: {content}")
            return content, ""
        
        # Validar contenido generado
        is_valid, problems = ContentValidator.validate_page_content(content)
        
        if not is_valid:
            logger.warning("Página generada con advertencias:")
            for problem in problems:
                logger.warning(f"  - {problem}")
        
        # Analizar calidad
        quality = self.page_generator.analyze_content_quality(content)
        logger.info(f"Calidad: {quality['word_count']} palabras, {quality['paragraph_count']} párrafos")
        
        # Guardar el contenido generado
        self._append_page_to_book(chapter_info, page_in_chapter, content)
        
        # Actualizar progreso
        if page_in_chapter >= total_pages:
            self._complete_chapter(chapter_info, content)
        else:
            self.memory['writing_progress']['current_page_in_chapter'] = page_in_chapter
        
        self.save_memory()
        
        status_msg = f"✅ Página {page_in_chapter}/{total_pages} del Cap. {chapter_info.get('number', 'N/A')} generada."
        return status_msg, content
    
    def _build_character_profiles(self, character_names: List[str]) -> str:
        """Construye perfiles de personajes para el prompt."""
        
        if not character_names:
            return ""
        
        profiles = []
        for name in character_names:
            char_data = self.memory.get('characters', {}).get(name, {})
            if char_data:
                profile = f"- **{name}:** {char_data.get('description', 'Sin descripción')}\n"
                profile += f"  Estado actual: {char_data.get('current_state', 'Desconocido')}"
                profiles.append(profile)
        
        return "\n".join(profiles) if profiles else ""
    
    def _get_last_written_text(self, char_limit: int = 1500) -> str:
        """Obtiene el último fragmento escrito del manuscrito."""
        
        if not self.book_file.exists():
            return ""
        
        try:
            with open(self.book_file, 'r', encoding='utf-8') as f:
                content = f.read()
                return content[-char_limit:] if content else ""
        except Exception as e:
            logger.error(f"Error al leer último texto: {e}")
            return ""
    
    def _append_page_to_book(self, chapter_info: Dict, page_number: int, content: str):
        """Añade una página al manuscrito."""
        
        try:
            with open(self.book_file, 'a', encoding='utf-8') as f:
                # Si es la primera página del capítulo, añadir título
                if page_number == 1:
                    chapter_title = f"\n\n## Capítulo {chapter_info.get('number', 'N/A')}: {chapter_info.get('title', 'Sin Título')}\n\n"
                    f.write(chapter_title)
                
                # Escribir contenido de la página
                f.write(f"{content}\n")
            
            logger.debug(f"Página añadida al manuscrito: {self.book_file}")
        except Exception as e:
            logger.error(f"Error al escribir página: {e}")
            raise
    
    def _complete_chapter(self, chapter_info: Dict, full_chapter_content: str):
        """Procesa la finalización de un capítulo."""
        
        logger.info(f"Finalizando capítulo {chapter_info.get('number', 'N/A')}")
        
        # Indexar capítulo en memoria semántica
        self._process_completed_chapter(chapter_info)
        
        # Actualizar estados de personajes
        self._update_character_states(chapter_info, full_chapter_content)
        
        # Guardar resumen del capítulo
        summary = {
            "number": chapter_info.get('number', 0),
            "title": chapter_info.get('title', ''),
            "summary": chapter_info.get('summary', '')
        }
        self.memory.setdefault('chapters_summary', []).append(summary)
        
        # Avanzar al siguiente capítulo
        self.memory['writing_progress']['current_chapter_index'] += 1
        self.memory['writing_progress']['current_page_in_chapter'] = 0
        
        logger.info(f"✅ Capítulo {chapter_info.get('number', 'N/A')} completado")
    
    def _process_completed_chapter(self, chapter_info: Dict):
        """Procesa y guarda el capítulo completado en la memoria semántica."""
        
        logger.info(f"Indexando capítulo {chapter_info.get('number', 'N/A')} en memoria semántica...")
        
        try:
            # Leer contenido completo del libro
            full_book_content = self.book_file.read_text(encoding='utf-8')
            
            # Extraer el capítulo específico
            chapter_header = f"## Capítulo {chapter_info.get('number', 'N/A')}: {chapter_info.get('title', 'Sin Título')}"
            next_chap_num = chapter_info.get('number', 0) + 1
            next_chap_header = re.compile(rf"## Capítulo {next_chap_num}:")
            
            start_index = full_book_content.rfind(chapter_header)
            if start_index == -1:
                logger.warning("No se pudo encontrar el capítulo en el manuscrito")
                return
            
            # Buscar inicio del siguiente capítulo
            match = next_chap_header.search(full_book_content, start_index)
            chapter_text = full_book_content[start_index:match.start()] if match else full_book_content[start_index:]
            
            # Añadir a memoria semántica
            self.semantic_memory.add_chapter(chapter_info.get('number', 0), chapter_text)
            
        except Exception as e:
            logger.error(f"Error al procesar capítulo para memoria semántica: {e}")
    
    def _update_character_states(self, chapter_info: Dict, chapter_content: str):
        """Actualiza el estado de los personajes después de un capítulo."""
        
        character_names = list(self.memory.get('characters', {}).keys())
        
        if not character_names:
            return
        
        logger.info("Actualizando estados de personajes...")
        
        # Obtener estados actuales
        current_states = {
            name: data.get('current_state', 'Desconocido')
            for name, data in self.memory.get('characters', {}).items()
        }
        
        # Actualizar usando el CharacterUpdater
        updated_states = self.character_updater.update_after_chapter(
            chapter_content=chapter_content,
            character_names=character_names,
            current_states=current_states
        )
        
        # Aplicar actualizaciones
        for char_name, new_state in updated_states.items():
            if char_name in self.memory['characters']:
                self.memory['characters'][char_name]['current_state'] = new_state
    
    # ========================================================================
    # ESCRITURA COMPLETA DEL LIBRO
    # ========================================================================
    
    def write_full_book(self) -> Generator[Tuple[float, str], None, None]:
        """
        Genera el libro completo página por página.
        
        Yields:
            Tupla (progreso: float, mensaje: str)
        """
        
        logger.info("=" * 60)
        logger.info("INICIANDO ESCRITURA COMPLETA DEL LIBRO")
        logger.info("=" * 60)
        
        # Calcular total de páginas
        outline = self.memory.get('plot', {}).get('outline', [])
        total_pages = sum(chap.get('pages_estimate', 10) for chap in outline)
        
        # Calcular páginas ya escritas
        status_dict = self.get_status()
        current_chap_idx = status_dict.get('current_chapter_number', 1) - 1
        pages_written = 0
        
        if current_chap_idx > 0:
            pages_written = sum(
                outline[i].get('pages_estimate', 10) 
                for i in range(current_chap_idx)
            )
        
        pages_written += status_dict.get('current_page', 1) - 1
        
        logger.info(f"Total de páginas estimadas: {total_pages}")
        logger.info(f"Páginas ya escritas: {pages_written}")
        
        # Generar páginas hasta completar
        while not self.get_status().get('completed', False):
            status_dict = self.get_status()
            
            progress_message = (
                f"Escribiendo pág. {status_dict.get('current_page')}/{status_dict.get('pages_in_chapter')} "
                f"del Cap. {status_dict.get('current_chapter_number')}..."
            )
            
            # Generar página
            status, _ = self.generate_page()
            
            if "Error" in status:
                logger.error(f"Error durante escritura: {status}")
                yield (pages_written / total_pages, f"❌ Error: {status}")
                return
            
            pages_written += 1
            progress = pages_written / total_pages
            
            yield (progress, progress_message)
            
            logger.info(f"Progreso: {progress*100:.1f}% ({pages_written}/{total_pages})")
            
            # Pausa entre páginas para evitar rate limits
            logger.info("Pausa de 10 segundos antes de la siguiente página...")
            time.sleep(10)
        
        # Libro completado
        logger.info("=" * 60)
        logger.info("✅ LIBRO COMPLETADO")
        logger.info("=" * 60)
        
        final_status_dict = self.get_status()
        final_status_text = self._format_status_display(final_status_dict)
        
        final_manuscript = ""
        if self.book_file.exists():
            final_manuscript = self.book_file.read_text(encoding='utf-8')
        
        yield (1.0, "✅ ¡Proceso de escritura finalizado!")
    
    # ========================================================================
    # GENERACIÓN DE BLURB Y PORTADA
    # ========================================================================
    
    def generate_book_blurb(self) -> str:
        """
        Genera el resumen de contraportada (blurb) del libro.
        
        Returns:
            Texto del blurb generado
        """
        
        logger.info("Generando blurb del libro...")
        
        metadata = self.memory.get('metadata', {})
        
        book_metadata = {
            'title': metadata.get('title', 'Sin Título'),
            'author_style': metadata.get('author_style', 'neutral'),
            'premise': self.memory.get('plot', {}).get('premise', ''),
            'themes': self.memory.get('plot', {}).get('themes', [])
        }
        
        # Construir prompt usando el PromptBuilder
        prompt = self.prompt_builder.build_blurb_prompt(book_metadata)
        
        # Generar blurb
        blurb = self._call_groq(prompt)
        
        # Validar blurb
        is_valid, problems = ContentValidator.validate_blurb(blurb)
        
        if not is_valid:
            logger.warning("Blurb generado con advertencias:")
            for problem in problems:
                logger.warning(f"  - {problem}")
        else:
            logger.info("✅ Blurb generado y validado")
        
        # Guardar en memoria
        self.memory['metadata']['blurb'] = blurb
        self.save_memory()
        
        return blurb
    
    def generate_cover_art(self) -> Tuple[Optional[str], str, str]:
        """
        Genera la portada del libro usando IA.
        
        Returns:
            Tupla (ruta_imagen, prompt_portada, mensaje_estado)
        """
        
        logger.info("Generando portada del libro...")
        
        # Asegurar que existe el blurb
        metadata = self.memory.get('metadata', {})
        if not metadata.get('blurb'):
            logger.info("Blurb no existe, generando primero...")
            self.generate_book_blurb()
            metadata['blurb'] = self.memory['metadata']['blurb']
        
        # Construir prompt para la portada usando templates
        from .prompts.templates import PromptTemplates
        
        prompt_for_main_image = PromptTemplates.cover_art_prompt(
            title=metadata.get('title', 'Sin Título'),
            author_style=metadata.get('author_style', 'neutral'),
            blurb=metadata.get('blurb', ''),
            themes=self.memory.get('plot', {}).get('themes', [])
        )
        
        # Generar el prompt artístico
        main_image_prompt = self._call_groq(prompt_for_main_image)
        
        # Guardar en memoria
        self.memory['metadata']['cover_prompt'] = main_image_prompt
        self.save_memory()
        
        logger.info(f"Prompt de portada generado: {main_image_prompt[:100]}...")
        
        # Prompt para el marco
        frame_prompt = (
            "An ornate, antique book cover frame in dark leather and carved wood. "
            "Intricate gold and silver filigree details in the corners. The center is completely transparent. "
            "Subtle realistic shadows. Photorealistic, 8k, cinematic lighting. "
            "The frame should look ancient and magical. 2:3 aspect ratio."
        )
        
        # Generar la imagen compuesta
        image_path, status = create_composite_cover(
            main_prompt=main_image_prompt,
            frame_prompt=frame_prompt,
            final_output_path=str(self.cover_file),
            temp_folder=str(self.project_path)
        )
        
        if image_path:
            logger.info(f"✅ Portada generada: {image_path}")
        else:
            logger.error(f"Error al generar portada: {status}")
        
        return image_path, main_image_prompt, status
    
    # ========================================================================
    # EXPORTACIÓN
    # ========================================================================
    
    def export_to_pdf(self) -> str:
        """
        Exporta el libro a formato PDF.
        
        Returns:
            Mensaje de resultado
        """
        
        logger.info("Exportando libro a PDF...")
        
        # Asegurar que existe el blurb
        if not self.memory.get('metadata', {}).get('blurb'):
            logger.info("Generando blurb antes de exportar...")
            self.generate_book_blurb()
        
        # Exportar usando el módulo existente
        result = export_book_to_pdf(
            pdf_path=str(self.pdf_file),
            book_file_path=str(self.book_file),
            memory=self.memory
        )
        
        if "✅" in result:
            logger.info(f"✅ PDF exportado: {self.pdf_file}")
        else:
            logger.error(f"Error al exportar PDF: {result}")
        
        return result
    
    # ========================================================================
    # ESTADO Y DIAGNÓSTICO
    # ========================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del proyecto.
        
        Returns:
            Diccionario con información de estado completa
        """
        
        progress = self.memory.get('writing_progress', {})
        outline = self.memory.get('plot', {}).get('outline', [])
        total_chapters = len(outline)
        current_idx = progress.get('current_chapter_index', 0)
        
        if total_chapters == 0:
            return {"message": "Aún no se ha generado un outline."}
        
        is_completed = current_idx >= total_chapters
        
        if is_completed:
            info = {"number": "N/A", "title": "Libro completado"}
            page, total_pages = 0, 0
        else:
            info = outline[current_idx]
            page = progress.get('current_page_in_chapter', 0) + 1
            total_pages = info.get('pages_estimate', 10)
        
        status_data = self.memory.get('metadata', {})
        
        return {
            "title": status_data.get('title', ''),
            "style": status_data.get('author_style', ''),
            "style_profile": status_data.get('style_profile', 'balanced_neutral'),
            "total_chapters": total_chapters,
            "current_chapter_number": info.get('number'),
            "current_chapter_title": info.get('title'),
            "current_page": page,
            "pages_in_chapter": total_pages,
            "characters": len(self.memory.get('characters', {})),
            "completed": is_completed,
            "ollama_status": self.semantic_memory.is_available,
            "blurb": status_data.get('blurb', ''),
            "cover_prompt": status_data.get('cover_prompt', ''),
            "cover_path": str(self.cover_file) if self.cover_file.exists() else None
        }
    
    def _format_status_display(self, status_dict: Dict) -> str:
        """Formatea el estado para display en UI."""
        
        if "message" in status_dict:
            return status_dict["message"]
        
        ollama_icon = "🟢" if status_dict.get("ollama_status") else "🔴"
        
        if status_dict.get('completed'):
            return f"""📖 **{status_dict['title']}**
---
✅ **LIBRO COMPLETADO**
---
✏️ Estilo: {status_dict['style']}
📚 Total Capítulos: {status_dict['total_chapters']}
🧠 Memoria a Largo Plazo (Ollama): {ollama_icon}"""
        
        return f"""📖 **{status_dict['title']}**
---
**Progreso Actual:**
- **Capítulo {status_dict['current_chapter_number']}:** "{status_dict['current_chapter_title']}"
- **Página:** {status_dict['current_page']} / {status_dict['pages_in_chapter']}
---
✏️ Estilo: {status_dict['style']}
📚 Total Capítulos: {status_dict['total_chapters']}
🧠 Memoria a Largo Plazo (Ollama): {ollama_icon}"""
    
    def generate_consistency_report(self) -> str:
        """
        Genera un reporte de consistencia del proyecto.
        
        Returns:
            Reporte formateado
        """
        
        logger.info("Generando reporte de consistencia...")
        
        report = ConsistencyValidator.generate_consistency_report(self.memory)
        
        logger.info("\n" + report)
        
        return report