import json
import re
from datetime import datetime
from typing import Dict, Tuple

# Importar configuraciones y cliente de Groq
from .config import (
    PROJECTS_PATH, MODEL, groq_client,
    TEMPERATURE, MAX_TOKENS, TOP_P, STOP_SEQUENCES
)
from .pdf_exporter import export_book_to_pdf
from .semantic_memory import SemanticMemory

class BookWriter:
    """
    Sistema de escritura de libros con memoria persistente y semántica para mantener
    una consistencia absoluta en la narrativa.
    """

    def __init__(self, project_name: str, author_style: str = "neutral"):
        self.project_name = self._sanitize_name(project_name)
        self.project_path = PROJECTS_PATH / self.project_name
        self.project_path.mkdir(exist_ok=True)

        # Rutas a los archivos del proyecto
        self.memory_file = self.project_path / 'memory.json'
        self.book_file = self.project_path / 'book.md'
        self.pdf_file = self.project_path / f'{self.project_name}.pdf'
        
        self.semantic_memory = SemanticMemory(self.project_path)

        # Estructura de la memoria
        self.memory = self._get_initial_memory(project_name, author_style)
        self.load_memory()

    def _get_initial_memory(self, project_name, author_style):
        """Devuelve la estructura inicial para el archivo de memoria JSON."""
        return {
            "metadata": {
                "title": project_name,
                "author_style": author_style,
                "created": datetime.now().isoformat(),
                "model": MODEL
            },
            "world": {},
            "characters": {},
            "plot": {"outline": [], "premise": "", "themes": []},
            "style": {},
            "chapters_summary": [],
            "consistency_rules": [],
            "writing_progress": {
                "current_chapter_index": 0,
                "current_page_in_chapter": 0
            }
        }

    def _sanitize_name(self, name: str) -> str:
        """Limpia un nombre para que sea seguro como nombre de directorio."""
        sanitized_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name).strip()
        sanitized_name = re.sub(r'_+', '_', sanitized_name)
        return sanitized_name

    def save_memory(self):
        """Guarda el estado actual de la memoria en el archivo JSON."""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=4)

    def load_memory(self):
        """Carga la memoria desde el archivo JSON si existe."""
        if self.memory_file.exists():
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                try:
                    self.memory = json.load(f)
                except json.JSONDecodeError:
                    print(f"Advertencia: El archivo memory.json para {self.project_name} está corrupto.")

    def _build_consistency_prompt(self) -> str:
        """Construye un prompt de sistema con la información clave del libro para mantener la consistencia."""
        plot_data = self.memory.get('plot', {})
        premise = plot_data.get('premise', 'No especificada')
        themes = ', '.join(plot_data.get('themes', []))

        return f"""Eres un escritor experto en el estilo de {self.memory.get('metadata', {}).get('author_style', 'neutral')}.
Tu tarea es escribir una novela manteniendo una consistencia absoluta con la información proporcionada.
Respeta los detalles del mundo, las personalidades de los personajes y la trama establecida.
NO inventes detalles que contradigan la memoria del libro.
---
**Título:** {self.memory.get('metadata', {}).get('title', 'Sin Título')}
**Premisa:** {premise}
**Temas:** {themes}
---"""

    def _call_groq(self, user_prompt: str) -> str:
        """Llama a la API de Groq con el contexto completo y los parámetros configurados."""
        try:
            system_prompt = self._build_consistency_prompt()
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
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Error en la llamada a Groq: {e}")
            return f"Error en la llamada a Groq: {e}"

    def generate_outline(self, premise: str, num_chapters: int, themes: str):
        """Genera el outline, mundo y personajes iniciales y los guarda en la memoria."""
        self.memory['plot']['premise'] = premise
        self.memory['plot']['themes'] = [theme.strip() for theme in themes.split(',')]
        
        prompt = f"""
Basado en la siguiente premisa, temas y estilo, genera un outline detallado para una novela de {num_chapters} capítulos.

**Premisa:** {premise}
**Temas:** {themes}
**Estilo de Autor Sugerido:** {self.memory['metadata']['author_style']}

Tu respuesta DEBE ser un único bloque de código JSON válido. No incluyas texto antes o después del JSON.
La estructura debe ser la siguiente:
{{
    "world": {{
        "setting": "Descripción detallada del mundo y la atmósfera.",
        "time_period": "Época o período en que transcurre la historia.",
        "key_locations": {{ "Nombre del Lugar": "Descripción breve" }},
        "rules_of_the_world": ["Regla 1 del universo", "Regla 2 del universo"]
    }},
    "characters": {{
        "Nombre del Personaje": {{
            "description": "Descripción física y de apariencia.",
            "personality": "Personalidad, motivaciones y miedos.",
            "story_arc": "Cómo evoluciona el personaje a lo largo de la historia.",
            "relationships": "Relaciones clave con otros personajes."
        }}
    }},
    "style": {{
        "tone": "Tono general de la narrativa (ej. sombrío, optimista, cínico).",
        "point_of_view": "Punto de vista (ej. Primera persona, Tercera persona limitada).",
        "tense": "Tiempo verbal predominante (ej. Pasado, Presente)."
    }},
    "plot": {{
        "outline": [
            {{
                "number": 1,
                "title": "Título del Capítulo",
                "summary": "Resumen detallado de lo que sucede en este capítulo.",
                "key_events": ["Evento importante 1", "Evento importante 2"],
                "character_focus": ["Personaje principal del capítulo"],
                "pages_estimate": 10
            }}
        ]
    }},
    "consistency_rules": ["Regla de consistencia 1 para la IA", "Regla 2"]
}}
"""
        response = self._call_groq(prompt)
        
        try:
            json_str = response.strip().replace("```json", "").replace("```", "")
            data = json.loads(json_str)

            self.memory['world'] = data.get('world', {})
            self.memory['characters'] = data.get('characters', {})
            self.memory['style'] = data.get('style', {})
            self.memory['consistency_rules'] = data.get('consistency_rules', [])
            
            plot_from_llm = data.get('plot', {})
            self.memory['plot']['outline'] = plot_from_llm.get('outline', [])
            
            for char_name, char_data in self.memory['characters'].items():
                char_data['current_state'] = "Al inicio de la historia."
            
            self.save_memory()
            return "✅ Outline, mundo y personajes generados con éxito."
        except json.JSONDecodeError as e:
            print(f"❌ Error al procesar la respuesta del modelo: {e}")
            return f"❌ Error al procesar la respuesta del modelo: {e}\n\nRespuesta recibida:\n{response[:500]}..."
        except Exception as e:
            print(f"❌ Error inesperado al generar el outline: {e}")
            return f"❌ Error inesperado: {e}"

    def generate_page(self) -> Tuple[str, str]:
        """Genera la siguiente página del libro basándose en el progreso actual."""
        progress = self.memory.get('writing_progress', {})
        current_chapter_index = progress.get('current_chapter_index', 0)
        
        outline = self.memory.get('plot', {}).get('outline', [])
        if not outline or current_chapter_index >= len(outline):
            return "✅ ¡Libro completado! Ya puedes exportarlo a PDF.", ""

        chapter_info = outline[current_chapter_index]
        page_in_chapter = progress.get('current_page_in_chapter', 0) + 1
        total_pages = chapter_info.get('pages_estimate', 10)

        # --- MEJORA DE CONSISTENCIA DE PERSONAJES ---
        character_focus_str = "No hay personajes específicos en foco para esta sección."
        focused_characters = chapter_info.get('character_focus', [])
        if focused_characters:
            char_profiles = []
            for char_name in focused_characters:
                char_data = self.memory.get('characters', {}).get(char_name)
                if char_data:
                    profile = f"- **{char_name}:** {char_data.get('description', '')} Personalidad: {char_data.get('personality', '')} Estado actual: {char_data.get('current_state', '')}"
                    char_profiles.append(profile)
            if char_profiles:
                character_focus_str = "\n".join(char_profiles)
        
        last_written_text = ""
        if self.book_file.exists():
            with open(self.book_file, 'r', encoding='utf-8') as f:
                last_written_text = f.read()[-1500:]

        query = last_written_text or chapter_info.get('summary', '')
        relevant_context = self.semantic_memory.search_relevant_context(query)

        # --- PROMPT REFORZADO Y SIMPLIFICADO ---
        prompt = f"""
**REGLAS CRÍTICAS E INELUDIBLES:**
1.  **FIDELIDAD ABSOLUTA A LOS PERSONAJES:** Usa los perfiles de personaje proporcionados en el Punto 1 de forma EXACTA. Es obligatorio que uses sus nombres, descripciones y personalidades tal como se definen. NO puedes inventar ni cambiar estos detalles bajo ninguna circunstancia.
2.  **NO REPETIR:** No repitas nada del "ÚLTIMO FRAGMENTO ESCRITO". Tu texto debe ser una continuación directa.

---

**1. PERFILES DE PERSONAJES EN FOCO PARA ESTA ESCENA:**
{character_focus_str}

**2. RESUMEN DEL CAPÍTULO ACTUAL (Nº {chapter_info.get('number', 'N/A')}: "{chapter_info.get('title', 'Sin Título')}")**:
{chapter_info.get('summary', '')}

**3. CONTEXTO DE CAPÍTULOS ANTERIORES (MEMORIA A LARGO PLAZO):**
{relevant_context}

**4. ÚLTIMO FRAGMENTO ESCRITO (MEMORIA A CORTO PLAZO):**
...{last_written_text}

---

**TU TAREA:**
Continúa la novela desde el final del "ÚLTIMO FRAGMENTO ESCRITO". Asegúrate de seguir las REGLAS CRÍTICAS y de avanzar en la trama descrita en el RESUMEN DEL CAPÍTULO. Escribe aproximadamente 400-500 palabras de narrativa fluida y coherente. No incluyas un título de capítulo en tu respuesta; el programa lo añadirá por ti.
"""
        page_content = self._call_groq(prompt)

        # --- GESTIÓN CENTRALIZADA DE TÍTULOS ---
        with open(self.book_file, 'a', encoding='utf-8') as f:
            if page_in_chapter == 1:
                # El código se encarga de escribir el título, no la IA.
                f.write(f"\n\n## Capítulo {chapter_info.get('number', 'N/A')}: {chapter_info.get('title', 'Sin Título')}\n\n")
            f.write(f"{page_content}\n")
        
        if page_in_chapter >= total_pages:
            self._process_completed_chapter(chapter_info)
            self._update_after_chapter_completion(chapter_info, page_content)
            self.memory['writing_progress']['current_chapter_index'] += 1
            self.memory['writing_progress']['current_page_in_chapter'] = 0
        else:
            self.memory['writing_progress']['current_page_in_chapter'] = page_in_chapter

        self.save_memory()
        status = f"✅ Página {page_in_chapter}/{total_pages} del Cap. {chapter_info.get('number', 'N/A')} generada."
        return status, page_content

    def _process_completed_chapter(self, chapter_info: dict):
        """Extrae el texto del capítulo recién completado y lo añade a la memoria semántica."""
        print(f"Finalizando capítulo {chapter_info.get('number', 'N/A')}. Indexando para memoria a largo plazo...")
        try:
            full_book_content = self.book_file.read_text(encoding='utf-8')
            chapter_header = f"## Capítulo {chapter_info.get('number', 'N/A')}: {chapter_info.get('title', 'Sin Título')}"
            
            next_chapter_index = chapter_info.get('number', 0)
            next_chapter_header_pattern = re.compile(rf"## Capítulo {next_chapter_index + 1}:")

            start_index = full_book_content.rfind(chapter_header)
            if start_index == -1:
                print(f"ADVERTENCIA: No se encontró el encabezado para el capítulo {chapter_info.get('number', 'N/A')}.")
                return

            match = next_chapter_header_pattern.search(full_book_content, start_index)
            if match:
                end_index = match.start()
                chapter_text = full_book_content[start_index:end_index]
            else:
                chapter_text = full_book_content[start_index:]
            
            self.semantic_memory.add_chapter(chapter_info.get('number', 0), chapter_text)

        except Exception as e:
            print(f"❌ Error al procesar el capítulo completado para la memoria semántica: {e}")

    def _update_after_chapter_completion(self, chapter_info, full_chapter_content):
        """Pide a la IA que actualice el estado de los personajes tras un capítulo."""
        prompt = f"""
Analiza el siguiente contenido del capítulo "{chapter_info.get('title', 'Sin Título')}" que acaba de terminar.
Basado en los eventos que ocurrieron, describe el nuevo estado (emocional, físico, situacional)
para cada uno de los personajes principales que aparecieron.

Contenido del capítulo:
---
{full_chapter_content[-2000:]}
---

Responde en un único bloque de código JSON, con la siguiente estructura:
{{
    "character_updates": {{
        "Nombre del Personaje 1": "Nuevo estado tras este capítulo.",
        "Nombre del Personaje 2": "Nuevo estado tras este capítulo."
    }}
}}
"""
        response = self._call_groq(prompt)
        try:
            json_str = response.strip().replace("```json", "").replace("```", "")
            data = json.loads(json_str)
            updates = data.get("character_updates", {})
            for char_name, new_state in updates.items():
                if char_name in self.memory.get('characters', {}):
                    self.memory['characters'][char_name]['current_state'] = new_state
                    print(f"🔄 Estado de '{char_name}' actualizado a: {new_state}")
        except Exception as e:
            print(f"⚠️ No se pudo actualizar el estado de los personajes: {e}")
        
        summary = {
            "number": chapter_info.get('number', 0),
            "title": chapter_info.get('title', 'Sin Título'),
            "summary": chapter_info.get('summary', '')
        }
        if 'chapters_summary' not in self.memory:
            self.memory['chapters_summary'] = []
        self.memory['chapters_summary'].append(summary)


    def export_to_pdf(self) -> str:
        """Exporta el manuscrito a un archivo PDF."""
        return export_book_to_pdf(
            pdf_path=str(self.pdf_file),
            book_file_path=str(self.book_file),
            metadata=self.memory.get('metadata', {}),
            chapters=self.memory.get('chapters_summary', [])
        )

    def get_status(self) -> dict:
        """Obtiene un diccionario con el estado actual del proyecto."""
        progress = self.memory.get('writing_progress', {})
        total_chapters = len(self.memory.get('plot', {}).get('outline', []))
        current_chapter_idx = progress.get('current_chapter_index', 0)
        
        if total_chapters == 0:
            return { "message": "Aún no se ha generado un outline para este proyecto."}
        
        is_completed = current_chapter_idx >= total_chapters
        
        if is_completed:
            current_chapter_info = {"number": "N/A", "title": "Libro completado"}
            page_in_chapter = 0
            pages_in_chapter = 0
        else:
            current_chapter_info = self.memory['plot']['outline'][current_chapter_idx]
            page_in_chapter = progress.get('current_page_in_chapter', 0) + 1
            pages_in_chapter = current_chapter_info.get('pages_estimate', 10)

        return {
            "title": self.memory.get('metadata', {}).get('title', 'Sin Título'),
            "style": self.memory.get('metadata', {}).get('author_style', 'neutral'),
            "total_chapters": total_chapters,
            "current_chapter_number": current_chapter_info.get('number'),
            "current_chapter_title": current_chapter_info.get('title'),
            "current_page": page_in_chapter,
            "pages_in_chapter": pages_in_chapter,
            "characters": len(self.memory.get('characters', {})),
            "completed": is_completed,
            "ollama_status": self.semantic_memory.is_available
        }

