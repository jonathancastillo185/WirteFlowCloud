import json
import re
from datetime import datetime
from typing import Dict, Tuple, Generator, Union, List
import time

# Importar configuraciones y funciones
from .config import (
    PROJECTS_PATH, MODEL, groq_client,
    TEMPERATURE, MAX_TOKENS, TOP_P, STOP_SEQUENCES
)
from .pdf_exporter import export_book_to_pdf
from .semantic_memory import SemanticMemory
from .image_generator import generate_image_with_stability

class BookWriter:
    # --- FUNCIÓN __INIT__ MODIFICADA ---
    def __init__(self, project_name: str, author_style: Union[str, List[str]] = "neutral"):
        self.project_name = self._sanitize_name(project_name)
        self.project_path = PROJECTS_PATH / self.project_name
        self.project_path.mkdir(exist_ok=True)

        # Rutas a los archivos del proyecto
        self.memory_file = self.project_path / 'memory.json'
        self.book_file = self.project_path / 'book.md'
        self.pdf_file = self.project_path / f'{self.project_name}.pdf'
        self.cover_file = self.project_path / 'cover.png'
        
        self.semantic_memory = SemanticMemory(self.project_path)

        # Convertir la lista de autores a un string si es necesario
        style_str = ", ".join(author_style) if isinstance(author_style, list) else author_style
        
        self.memory = self._get_initial_memory(project_name, style_str)
        self.load_memory()

    def _get_initial_memory(self, project_name, author_style):
        # ... (el resto del archivo no necesita cambios)
        return {
            "metadata": {
                "title": project_name, "author_style": author_style,
                "created": datetime.now().isoformat(), "model": MODEL,
                "blurb": "", "cover_prompt": ""
            },
            "world": {}, "characters": {},
            "plot": {"outline": [], "premise": "", "themes": []},
            "style": {}, "chapters_summary": [], "consistency_rules": [],
            "writing_progress": {"current_chapter_index": 0, "current_page_in_chapter": 0}
        }
    
    def _sanitize_name(self, name: str) -> str:
        sanitized_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name).strip()
        return re.sub(r'_+', '_', sanitized_name)

    def save_memory(self):
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=4)

    def load_memory(self):
        if self.memory_file.exists():
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                try:
                    loaded_memory = json.load(f)
                    loaded_memory.setdefault('metadata', {}).setdefault('blurb', "")
                    loaded_memory.setdefault('metadata', {}).setdefault('cover_prompt', "")
                    self.memory = loaded_memory
                except json.JSONDecodeError:
                    print(f"Advertencia: El archivo memory.json para {self.project_name} está corrupto.")

    def _build_consistency_prompt(self) -> str:
        plot_data = self.memory.get('plot', {})
        return f"""Eres un escritor experto en el estilo de {self.memory.get('metadata', {}).get('author_style', 'neutral')}.
Tu tarea es escribir una novela manteniendo una consistencia absoluta.
Respeta los detalles del mundo, las personalidades de los personajes y la trama establecida.
---
**Título:** {self.memory.get('metadata', {}).get('title', 'Sin Título')}
**Premisa:** {plot_data.get('premise', 'No especificada')}
**Temas:** {', '.join(plot_data.get('themes', []))}
---"""

    def _call_groq(self, user_prompt: str) -> str:
        max_retries = 5
        for attempt in range(max_retries):
            try:
                system_prompt = self._build_consistency_prompt()
                response = groq_client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=TEMPERATURE, max_tokens=MAX_TOKENS,
                    top_p=TOP_P, stop=STOP_SEQUENCES
                )
                return response.choices[0].message.content
            except Exception as e:
                if "429" in str(e) and "rate_limit_exceeded" in str(e):
                    wait_match = re.search(r"Please try again in ([\d.]+)s", str(e))
                    if wait_match:
                        wait_seconds = float(wait_match.group(1)) + 1
                        print(f"🔶 Límite de tasa alcanzado. Esperando {wait_seconds:.2f} segundos...")
                        time.sleep(wait_seconds)
                        continue
                print(f"❌ Error en la llamada a Groq (intento {attempt + 1}/{max_retries}): {e}")
                if attempt + 1 == max_retries:
                    return f"Error en la llamada a Groq tras {max_retries} intentos: {e}"
        return f"Error: No se pudo completar la llamada a Groq tras {max_retries} reintentos."

    def generate_outline(self, premise: str, num_chapters: int, themes: str):
        self.memory['plot']['premise'] = premise
        self.memory['plot']['themes'] = [theme.strip() for theme in themes.split(',')]
        prompt = f"""
Basado en la siguiente premisa, temas y estilo, genera un outline detallado para una novela de {num_chapters} capítulos.
**Premisa:** {premise}
**Temas:** {themes}
**Estilo Sugerido:** {self.memory['metadata']['author_style']}
Tu respuesta DEBE ser un único JSON válido con la siguiente estructura:
{{
    "world": {{"setting": "...", "time_period": "...", "key_locations": {{}}, "rules_of_the_world": []}},
    "characters": {{"Nombre": {{"description": "...", "personality": "...", "story_arc": "...", "relationships": "..."}}}},
    "style": {{"tone": "...", "point_of_view": "...", "tense": "..."}},
    "plot": {{"outline": [{{"number": 1, "title": "...", "summary": "...", "key_events": [], "character_focus": [], "pages_estimate": 10}}]}},
    "consistency_rules": []
}}
"""
        response = self._call_groq(prompt)
        try:
            data = json.loads(response.strip().replace("```json", "").replace("```", ""))
            self.memory.update(data)
            self.memory['plot']['outline'] = data.get('plot', {}).get('outline', [])
            for char_name, char_data in self.memory['characters'].items():
                char_data['current_state'] = "Al inicio de la historia."
            self.save_memory()
            return "✅ Outline, mundo y personajes generados con éxito."
        except Exception as e:
            return f"❌ Error al procesar la respuesta del modelo: {e}\nRespuesta recibida:\n{response[:500]}..."

    def generate_book_blurb(self) -> str:
        print("Generando resumen del libro...")
        metadata = self.memory.get('metadata', {})
        plot_data = self.memory.get('plot', {})
        prompt = f"""
Actúa como un editor experto. Escribe un resumen de contraportada (blurb) intrigante y comercial para la novela.
- **Título:** {metadata.get('title', 'Sin Título')}
- **Estilo:** {metadata.get('author_style', 'neutral')}
- **Premisa:** {plot_data.get('premise', '')}
- **Temas:** {', '.join(plot_data.get('themes', []))}
**Instrucciones:** Tono acorde al género. No reveles el final. 150-200 palabras. Responde solo con el texto del resumen.
"""
        blurb = self._call_groq(prompt)
        self.memory['metadata']['blurb'] = blurb
        self.save_memory()
        return blurb

    def generate_cover_art(self) -> tuple[str | None, str, str]:
        print("✍️ Generando prompt artístico para la portada...")
        metadata = self.memory.get('metadata', {})
        if not metadata.get('blurb'):
            self.generate_book_blurb()
            metadata['blurb'] = self.memory['metadata']['blurb']
        prompt_for_prompt = f"""
Actúa como un director de arte. Escribe un prompt detallado para un modelo de IA de texto a imagen.
- **Título:** {metadata.get('title', 'Sin Título')}
- **Estilo:** {metadata.get('author_style', 'neutral')}
- **Resumen:** {metadata.get('blurb', '')}
- **Temas:** {', '.join(self.memory.get('plot', {}).get('themes', []))}
**Instrucciones:**
1. Describe la escena, personajes, atmósfera, estilo, iluminación y colores. Usa adjetivos potentes.
2. **CRÍTICO: El prompt final DEBE ESTAR ESCRITO EN INGLÉS.** La IA de imagen solo entiende inglés.
3. Responde únicamente con el texto del prompt.

Ejemplo de salida en INGLÉS: "Epic digital painting of a lone astronaut on the edge of a Martian canyon under a crimson sky. Cinematic style, high resolution."
"""
        cover_prompt = self._call_groq(prompt_for_prompt)
        self.memory['metadata']['cover_prompt'] = cover_prompt
        self.save_memory()
        image_path, status = generate_image_with_stability(cover_prompt, str(self.cover_file))
        return image_path, cover_prompt, status
    
    def write_full_book(self) -> Generator[Tuple[float, str], None, None]:
        total_pages = sum(chap.get('pages_estimate', 10) for chap in self.memory.get('plot', {}).get('outline', []))
        pages_written = 0
        status_dict = self.get_status()
        current_chap_idx = status_dict.get('current_chapter_number', 1) - 1
        if current_chap_idx > 0:
            pages_written = sum(self.memory['plot']['outline'][i].get('pages_estimate', 10) for i in range(current_chap_idx))
        pages_written += status_dict.get('current_page', 1) - 1
        
        while not self.get_status().get('completed', False):
            status_dict = self.get_status()
            progress_message = f"Escribiendo pág. {status_dict.get('current_page')}/{status_dict.get('pages_in_chapter')} del Cap. {status_dict.get('current_chapter_number')}..."
            status, _ = self.generate_page()
            if "Error" in status:
                yield (pages_written / total_pages, f"❌ Error: {status}")
                return
            pages_written += 1
            yield (pages_written / total_pages, progress_message)
        yield (1.0, "✅ ¡Libro completado!")

    def generate_page(self) -> Tuple[str, str]:
        progress = self.memory.get('writing_progress', {})
        outline = self.memory.get('plot', {}).get('outline', [])
        current_chapter_index = progress.get('current_chapter_index', 0)
        if not outline or current_chapter_index >= len(outline):
            return "✅ ¡Libro completado!", ""
        
        chapter_info = outline[current_chapter_index]
        page_in_chapter = progress.get('current_page_in_chapter', 0) + 1
        total_pages = chapter_info.get('pages_estimate', 10)
        
        char_profiles = [f"- **{name}:** {self.memory.get('characters',{}).get(name,{}).get('description','')} Personalidad: {self.memory.get('characters',{}).get(name,{}).get('personality','')} Estado: {self.memory.get('characters',{}).get(name,{}).get('current_state','')}" for name in chapter_info.get('character_focus', [])]
        character_focus_str = "\n".join(char_profiles) if char_profiles else "No hay personajes específicos en foco."
        
        last_written_text = ""
        if self.book_file.exists():
            with open(self.book_file, 'r', encoding='utf-8') as f: last_written_text = f.read()[-1500:]
        
        query = last_written_text or chapter_info.get('summary', '')
        relevant_context = self.semantic_memory.search_relevant_context(query)
        
        prompt = f"""
**REGLAS CRÍTICAS:**
1. **FIDELIDAD ABSOLUTA A LOS PERSONAJES:** Usa los perfiles del Punto 1 EXACTAMENTE. NO puedes cambiar nombres o personalidades.
2. **NO REPETIR:** Continúa la historia desde el "ÚLTIMO FRAGMENTO ESCRITO".
---
**1. PERFILES DE PERSONAJES:**
{character_focus_str}
**2. RESUMEN DEL CAPÍTULO (Nº {chapter_info.get('number', 'N/A')}: "{chapter_info.get('title', 'Sin Título')}")**:
{chapter_info.get('summary', '')}
**3. CONTEXTO DE CAPÍTULOS ANTERIORES:**
{relevant_context}
**4. ÚLTIMO FRAGMENTO ESCRITO:**
...{last_written_text}
---
**TU TAREA:** Continúa la novela desde el final del "ÚLTIMO FRAGMENTO ESCRITO". Sigue las REGLAS y la trama. Escribe 400-500 palabras. No incluyas un título.
"""
        page_content = self._call_groq(prompt)
        if "Error" in page_content:
            return page_content, ""

        with open(self.book_file, 'a', encoding='utf-8') as f:
            if page_in_chapter == 1:
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
        return f"✅ Página {page_in_chapter}/{total_pages} del Cap. {chapter_info.get('number', 'N/A')} generada.", page_content

    def _process_completed_chapter(self, chapter_info: dict):
        print(f"Finalizando capítulo {chapter_info.get('number', 'N/A')}. Indexando...")
        try:
            full_book_content = self.book_file.read_text(encoding='utf-8')
            chapter_header = f"## Capítulo {chapter_info.get('number', 'N/A')}: {chapter_info.get('title', 'Sin Título')}"
            next_chap_num = chapter_info.get('number', 0) + 1
            next_chap_header = re.compile(rf"## Capítulo {next_chap_num}:")
            start_index = full_book_content.rfind(chapter_header)
            if start_index == -1: return
            match = next_chap_header.search(full_book_content, start_index)
            chapter_text = full_book_content[start_index:match.start()] if match else full_book_content[start_index:]
            self.semantic_memory.add_chapter(chapter_info.get('number', 0), chapter_text)
        except Exception as e:
            print(f"❌ Error al procesar capítulo para memoria semántica: {e}")

    def _update_after_chapter_completion(self, chapter_info, full_chapter_content):
        prompt = f"""
Analiza el contenido del capítulo "{chapter_info.get('title', 'Sin Título')}" y describe el nuevo estado de los personajes.
Contenido: --- {full_chapter_content[-2000:]} ---
Responde en JSON: {{"character_updates": {{"Nombre": "Nuevo estado."}}}}
"""
        response = self._call_groq(prompt)
        try:
            data = json.loads(response.strip().replace("```json", "").replace("```", ""))
            updates = data.get("character_updates", {})
            for char, state in updates.items():
                if char in self.memory.get('characters', {}):
                    self.memory['characters'][char]['current_state'] = state
                    print(f"🔄 Estado de '{char}' actualizado a: {state}")
        except Exception as e:
            print(f"⚠️ No se pudo actualizar estado de personajes: {e}")
        summary = {"number": chapter_info.get('number',0), "title": chapter_info.get('title',''), "summary": chapter_info.get('summary','')}
        self.memory.setdefault('chapters_summary', []).append(summary)

    def export_to_pdf(self) -> str:
        if not self.memory.get('metadata', {}).get('blurb'):
            self.generate_book_blurb()
        return export_book_to_pdf(pdf_path=str(self.pdf_file), book_file_path=str(self.book_file), memory=self.memory)
    
    def get_status(self) -> dict:
        progress = self.memory.get('writing_progress', {})
        outline = self.memory.get('plot', {}).get('outline', [])
        total_chapters = len(outline)
        current_idx = progress.get('current_chapter_index', 0)
        if total_chapters == 0: return {"message": "Aún no se ha generado un outline."}
        is_completed = current_idx >= total_chapters
        info = outline[current_idx] if not is_completed else {"number": "N/A", "title": "Libro completado"}
        page, total_pages = (progress.get('current_page_in_chapter', 0) + 1, info.get('pages_estimate', 10)) if not is_completed else (0, 0)
        
        status_data = self.memory.get('metadata',{})
        return {
            "title": status_data.get('title',''), "style": status_data.get('author_style',''),
            "total_chapters": total_chapters, "current_chapter_number": info.get('number'),
            "current_chapter_title": info.get('title'), "current_page": page,
            "pages_in_chapter": total_pages, "characters": len(self.memory.get('characters',{})),
            "completed": is_completed, "ollama_status": self.semantic_memory.is_available,
            "blurb": status_data.get('blurb',''), "cover_prompt": status_data.get('cover_prompt',''),
            "cover_path": str(self.cover_file) if self.cover_file.exists() else None
        }

