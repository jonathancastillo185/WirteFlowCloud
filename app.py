import gradio as gr
from bookwriter.core import BookWriter
from bookwriter.config import PROJECTS_PATH
import os
import time

# --- Estado Global ---
active_project_state = {"book": None}

# --- Funciones de Utilidad ---
def get_project_list():
    """Obtiene y devuelve la lista de proyectos existentes."""
    if not PROJECTS_PATH.exists():
        PROJECTS_PATH.mkdir()
    return [d.name for d in PROJECTS_PATH.iterdir() if d.is_dir()]

def update_status_display(status_dict: dict) -> str:
    """Formatea el diccionario de estado en un string legible para la UI."""
    if "message" in status_dict:
        return status_dict["message"]
    ollama_icon = "🟢" if status_dict.get("ollama_status") else "🔴"
    if status_dict.get('completed'):
        return f"📖 **{status_dict['title']}**\n---\n✅ **LIBRO COMPLETADO**\n---\n✍️ Estilo: {status_dict['style']}\n📚 Total Capítulos: {status_dict['total_chapters']}\n🧠 Memoria a Largo Plazo (Ollama): {ollama_icon}"
    return f"📖 **{status_dict['title']}**\n---\n**Progreso Actual:**\n- **Capítulo {status_dict['current_chapter_number']}:** \"{status_dict['current_chapter_title']}\"\n- **Página:** {status_dict['current_page']} / {status_dict['pages_in_chapter']}\n---\n✍️ Estilo: {status_dict['style']}\n📚 Total Capítulos: {status_dict['total_chapters']}\n🧠 Memoria a Largo Plazo (Ollama): {ollama_icon}"

# --- Funciones de Lógica de la Interfaz ---
def load_project(project_name: str):
    """Carga un proyecto y actualiza todos los componentes de la UI."""
    if not project_name:
        return "Selecciona un proyecto.", {}, "", "", "", "", None, gr.update(choices=get_project_list())
    print(f"Cargando proyecto: {project_name}...")
    book = BookWriter(project_name)
    active_project_state["book"] = book
    status_dict = book.get_status()
    status_text = update_status_display(status_dict)
    manuscript_content = ""
    if book.book_file.exists():
        manuscript_content = book.book_file.read_text(encoding='utf-8')
    blurb = status_dict.get('blurb', 'Aún no se ha generado un resumen.')
    cover_prompt = status_dict.get('cover_prompt', 'Aún no se ha generado un prompt para la portada.')
    cover_image = status_dict.get('cover_path')
    return status_text, book.memory, manuscript_content, "", blurb, cover_prompt, cover_image

def create_project(name: str, premise: str, chapters: int, themes: str, authors: list, progress=gr.Progress(track_tqdm=True)):
    """Crea un nuevo proyecto y genera su outline."""
    if not all([name, premise, chapters, themes, authors]):
        return "Por favor, completa todos los campos y selecciona al menos un autor.", gr.update(choices=get_project_list())
    progress(0, desc="Inicializando proyecto...")
    book = BookWriter(name, authors)
    active_project_state["book"] = book
    progress(0.5, desc="Generando outline con IA...")
    result = book.generate_outline(premise, int(chapters), themes)
    time.sleep(1)
    progress(1, desc="¡Outline generado!")
    project_list = get_project_list()
    return result, gr.update(choices=project_list, value=book.project_name)

def generate_blurb_interface(progress=gr.Progress(track_tqdm=True)):
    """Función de interfaz para generar el blurb."""
    book = active_project_state.get("book")
    if not book: return "Carga un proyecto primero.", {}
    progress(0.5, desc="Generando resumen con IA...")
    blurb = book.generate_book_blurb()
    progress(1, desc="¡Resumen generado!")
    return blurb, book.memory

def generate_cover_interface(progress=gr.Progress(track_tqdm=True)):
    """Función de interfaz para generar la portada."""
    book = active_project_state.get("book")
    if not book: return None, "Carga un proyecto primero.", "", {}
    progress(0, desc="Paso 1/2: Creando prompt artístico...")
    image_path, cover_prompt, status = book.generate_cover_art()
    if image_path:
        progress(1, desc="Paso 2/2: ¡Portada generada!")
    else:
        progress(1, desc="Error al generar portada.")
    return image_path, cover_prompt, status, book.memory

def write_full_book_interface(progress=gr.Progress(track_tqdm=True)):
    """Función de interfaz para escribir el libro completo."""
    book = active_project_state.get("book")
    if not book:
        return "Carga un proyecto primero.", "", "", "", {}, gr.update(choices=get_project_list())
    try:
        for percentage, message in book.write_full_book():
            progress(percentage, desc=message)
            yield message, gr.update(), gr.update(), gr.update(), gr.update(), gr.update()
    except Exception as e:
        print(f"Error durante la escritura del libro: {e}")
    print("Refrescando la interfaz tras la escritura completa.")
    final_status_dict = book.get_status()
    final_status_text = update_status_display(final_status_dict)
    final_manuscript = book.book_file.read_text(encoding='utf-8') if book.book_file.exists() else ""
    yield ("✅ ¡Proceso de escritura finalizado!", final_status_text, final_manuscript, "", book.memory, gr.update(choices=get_project_list(), value=book.project_name))

def generate_next_page():
    """Genera la siguiente página del libro."""
    book = active_project_state.get("book")
    if not book: return "Carga un proyecto primero.", "", "", "", {}
    status_update, page_content = book.generate_page()
    manuscript_content = ""
    if book.book_file.exists():
        manuscript_content = book.book_file.read_text(encoding='utf-8')
    status_dict = book.get_status()
    status_text = update_status_display(status_dict)
    return status_update, status_text, manuscript_content, page_content, book.memory

def export_pdf(progress=gr.Progress(track_tqdm=True)):
    """Exporta el libro a PDF."""
    book = active_project_state.get("book")
    if not book: return "Carga un proyecto primero."
    progress(0.5, desc="Generando archivo PDF...")
    result = book.export_to_pdf()
    progress(1, desc="¡PDF Exportado!")
    return result

def refresh_all_views(project_name: str):
    """Función unificada para refrescar todas las vistas."""
    if not project_name:
        return "Selecciona un proyecto.", {}, "", "", "Carga un proyecto.", "", None
    return load_project(project_name)

# --- Construcción de la Interfaz ---
with gr.Blocks(theme=gr.themes.Soft(), title="BookWriter AI") as app:
    gr.Markdown("# 📚 BookWriter AI - Tu Asistente de Escritura Local")

    # --- LISTA DE AUTORES CORREGIDA PARA VISUALIZACIÓN ---
    # El formato (Texto a mostrar, Valor a enviar) es el más robusto para multiselect.
    author_choices = [
        # Terror
        ("Terror / Horror: Stephen King", "Stephen King"),
        ("Terror / Horror: H.P. Lovecraft", "H.P. Lovecraft"),
        ("Terror / Horror: Edgar Allan Poe", "Edgar Allan Poe"),
        ("Terror / Horror: Shirley Jackson", "Shirley Jackson"),
        ("Terror / Horror: Mary Shelley", "Mary Shelley"),
        ("Terror / Horror: Bram Stoker", "Bram Stoker"),
        # Aventura
        ("Aventura: Jules Verne", "Jules Verne"),
        ("Aventura: Robert Louis Stevenson", "Robert Louis Stevenson"),
        ("Aventura: Jack London", "Jack London"),
        ("Aventura: Emilio Salgari", "Emilio Salgari"),
        ("Aventura: Alexandre Dumas", "Alexandre Dumas"),
        ("Aventura: J.K. Rowling", "J.K. Rowling"),
        ("Aventura: Maria Elena Walsh", "Maria Elena Wcalsh"),
        # Romance
        ("Romance: Jane Austen", "Jane Austen"),
        ("Romance: Nicholas Sparks", "Nicholas Sparks"),
        ("Romance: Nora Roberts", "Nora Roberts"),
        ("Romance: Julia Quinn", "Julia Quinn"),
        ("Romance: Emily Brontë", "Emily Brontë"),
        ("Romance: Gabriel García Márquez", "Gabriel García Márquez"),
        # Ciencia Ficción
        ("Ciencia Ficción: Isaac Asimov", "Isaac Asimov"),
        ("Ciencia Ficción: Philip K. Dick", "Philip K. Dick"),
        ("Ciencia Ficción: Ursula K. Le Guin", "Ursula K. Le Guin"),
        ("Ciencia Ficción: Frank Herbert", "Frank Herbert"),
        ("Ciencia Ficción: Arthur C. Clarke", "Arthur C. Clarke"),
        # Fantasía
        ("Fantasía: J.R.R. Tolkien", "J.R.R. Tolkien"),
        ("Fantasía: George R.R. Martin", "George R.R. Martin"),
        ("Fantasía: Brandon Sanderson", "Brandon Sanderson"),
        ("Fantasía: Neil Gaiman", "Neil Gaiman"),
        ("Fantasía: C.S. Lewis", "C.S. Lewis"),
        # Misterio / Thriller
        ("Misterio / Thriller: Agatha Christie", "Agatha Christie"),
        ("Misterio / Thriller: Arthur Conan Doyle", "Arthur Conan Doyle"),
        ("Misterio / Thriller: Gillian Flynn", "Gillian Flynn"),
        ("Misterio / Thriller: Raymond Chandler", "Raymond Chandler"),
        # Clásicos / Literarios
        ("Clásicos / Literarios: Jorge Luis Borges", "Jorge Luis Borges"),
        ("Clásicos / Literarios: Ernest Hemingway", "Ernest Hemingway"),
        ("Clásicos / Literarios: Virginia Woolf", "Virginia Woolf"),
        ("Clásicos / Literarios: Fiodor Dostoievski", "Fiodor Dostoievski"),
        # Filosofía / Ensayo
        ("Filosofía / Ensayo: Friedrich Nietzsche", "Friedrich Nietzsche"),
        ("Filosofía / Ensayo: Simone de Beauvoir", "Simone de Beauvoir"),
        ("Filosofía / Ensayo: Yuval Noah Harari", "Yuval Noah Harari"),
        # Psicología / Auto-ayuda
        ("Psicología / Auto-ayuda: Carl Jung", "Carl Jung"),
        ("Psicología / Auto-ayuda: Jordan Peterson", "Jordan Peterson"),
        ("Psicología / Auto-ayuda: Brené Brown", "Brené Brown"),
        ("Psicología / Auto-ayuda: Mark Manson", "Mark Manson"),
    ]

    with gr.Tab("🚀 Gestión de Proyectos"):
        gr.Markdown("### Cargar un Proyecto Existente")
        with gr.Row():
            project_select = gr.Dropdown(choices=get_project_list(), label="Proyectos Guardados", interactive=True)
            load_btn = gr.Button("Cargar Proyecto", variant="secondary")
        
        gr.Markdown("---")
        
        gr.Markdown("### Crear un Nuevo Proyecto")
        with gr.Row():
            new_name = gr.Textbox(label="Título del Libro")
            author_style = gr.Dropdown(
                label="Inspirado en el Estilo de (elige uno o más)",
                choices=author_choices,
                multiselect=True,
                interactive=True
            )
        premise = gr.Textbox(label="Premisa / Sinopsis", lines=3)
        with gr.Row():
            num_chapters = gr.Slider(3, 50, 15, step=1, label="Número de Capítulos")
            themes = gr.Textbox(label="Temas (separados por comas)", placeholder="ej. soledad, supervivencia")
        create_btn = gr.Button("Crear y Generar Outline", variant="primary")
        status_create = gr.Textbox(label="Estado de Creación", interactive=False)
        
    with gr.Tab("✍️ Escritura y Exportación"):
        status_display = gr.Textbox(label="Estado del Proyecto", lines=8, interactive=False)
        with gr.Row():
            gen_page_btn = gr.Button("📄 Generar Página Siguiente", variant="secondary", scale=1)
            write_full_book_btn = gr.Button("📚 Escribir Libro Completo", variant="primary", scale=2)
            export_btn = gr.Button("📥 Exportar a PDF", variant="secondary", scale=1)
            
        last_page = gr.Textbox(label="Última Página Generada", lines=15, interactive=False)
        export_status = gr.Textbox(label="Estado de Exportación", interactive=False)
        
        gr.Markdown("---")
        gr.Markdown("### Resumen y Portada")
        with gr.Row():
            with gr.Column(scale=2):
                blurb_display = gr.Textbox(label="Resumen de Contraportada", lines=7, interactive=False)
                gen_blurb_btn = gr.Button("✨ Generar / Regenerar Resumen", variant="secondary")
                cover_prompt_display = gr.Textbox(label="Prompt Artístico para Portada", lines=4, interactive=False)
                gen_cover_btn = gr.Button("🎨 Generar Portada con IA", variant="primary")
                cover_status = gr.Textbox(label="Estado de la Portada", interactive=False)
            with gr.Column(scale=1):
                cover_image_display = gr.Image(label="Portada Generada", type="filepath", interactive=False)

    with gr.Tab("📖 Manuscrito Completo"):
        book_display = gr.Markdown("Carga un proyecto para ver el manuscrito.")
        refresh_book_btn = gr.Button("🔄 Actualizar Vista")
        
    with gr.Tab("🧠 Memoria del Proyecto"):
        memory_display = gr.JSON(label="Memoria Completa del Proyecto")
        refresh_memory_btn = gr.Button("🔄 Actualizar Vista")

    # --- Conexiones de Eventos ---
    outputs_on_load = [status_display, memory_display, book_display, last_page, blurb_display, cover_prompt_display, cover_image_display]
    app.load(get_project_list, outputs=project_select)
    create_btn.click(fn=create_project, inputs=[new_name, premise, num_chapters, themes, author_style], outputs=[status_create, project_select])
    load_btn.click(fn=refresh_all_views, inputs=[project_select], outputs=outputs_on_load)
    refresh_book_btn.click(fn=refresh_all_views, inputs=[project_select], outputs=outputs_on_load)
    refresh_memory_btn.click(fn=refresh_all_views, inputs=[project_select], outputs=outputs_on_load)
    project_select.change(fn=refresh_all_views, inputs=[project_select], outputs=outputs_on_load)
    gen_page_btn.click(fn=generate_next_page, outputs=[status_create, status_display, book_display, last_page, memory_display])
    gen_blurb_btn.click(fn=generate_blurb_interface, outputs=[blurb_display, memory_display])
    gen_cover_btn.click(fn=generate_cover_interface, outputs=[cover_image_display, cover_prompt_display, cover_status, memory_display])
    write_full_book_btn.click(fn=write_full_book_interface, outputs=[status_create, status_display, book_display, last_page, memory_display, project_select])
    export_btn.click(export_pdf, outputs=[export_status])

if __name__ == "__main__":
    app.launch()

