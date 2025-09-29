import gradio as gr
from bookwriter.core import BookWriter
from bookwriter.config import PROJECTS_PATH
import os
import time

# --- Estado Global ---
# Usamos un diccionario para mantener el estado del proyecto activo.
active_project_state = {"book": None}

# --- Funciones de Utilidad para la Interfaz ---

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
        return f"""
📖 **{status_dict['title']}**
---
✅ **LIBRO COMPLETADO**
---
✍️ Estilo: {status_dict['style']}
📚 Total Capítulos: {status_dict['total_chapters']}
🧠 Memoria a Largo Plazo (Ollama): {ollama_icon}
"""

    return f"""
📖 **{status_dict['title']}**
---
**Progreso Actual:**
- **Capítulo {status_dict['current_chapter_number']}:** "{status_dict['current_chapter_title']}"
- **Página:** {status_dict['current_page']} / {status_dict['pages_in_chapter']}
---
✍️ Estilo: {status_dict['style']}
📚 Total Capítulos: {status_dict['total_chapters']}
🧠 Memoria a Largo Plazo (Ollama): {ollama_icon}
"""


# --- Funciones de Lógica de la Interfaz (Conectadas a los Eventos de Gradio) ---

def load_project(project_name: str):
    """Carga un proyecto existente y actualiza la interfaz."""
    if not project_name:
        return "Selecciona un proyecto para cargarlo.", {}, "", "", gr.update(choices=get_project_list())

    print(f"Cargando proyecto: {project_name}...")
    book = BookWriter(project_name)
    active_project_state["book"] = book
    
    status_dict = book.get_status()
    status_text = update_status_display(status_dict)
    
    manuscript_content = ""
    if book.book_file.exists():
        manuscript_content = book.book_file.read_text(encoding='utf-8')
    
    return status_text, book.memory, manuscript_content, ""

def create_project(name: str, premise: str, chapters: int, themes: str, author: str, progress=gr.Progress(track_tqdm=True)):
    """Crea un nuevo proyecto y genera su outline."""
    if not all([name, premise, chapters, themes, author]):
        return "Por favor, completa todos los campos para crear un proyecto.", gr.update(choices=get_project_list())

    progress(0, desc="Inicializando proyecto...")
    book = BookWriter(name, author)
    active_project_state["book"] = book
    
    progress(0.5, desc="Generando outline con IA (puede tardar un momento)...")
    result = book.generate_outline(premise, int(chapters), themes)
    
    time.sleep(1) # Pequeña pausa para que el usuario vea el resultado
    progress(1, desc="¡Outline generado!")

    # Actualizamos la lista de proyectos en el dropdown
    project_list = get_project_list()
    
    # --- CORRECCIÓN CLAVE ---
    # Devolvemos el nombre del proyecto YA SANITIZADO (book.project_name)
    # en lugar del 'name' original con espacios.
    return result, gr.update(choices=project_list, value=book.project_name)

def generate_next_page():
    """Genera la siguiente página del libro y actualiza los componentes de la UI."""
    book = active_project_state.get("book")
    if not book:
        return "Carga un proyecto primero.", "", "", "", {}

    status_update, page_content = book.generate_page()
    
    manuscript_content = ""
    if book.book_file.exists():
        manuscript_content = book.book_file.read_text(encoding='utf-8')
    
    status_dict = book.get_status()
    status_text = update_status_display(status_dict)
    
    return status_update, status_text, manuscript_content, page_content, book.memory

def export_pdf():
    """Exporta el libro actual a formato PDF."""
    book = active_project_state.get("book")
    if not book:
        return "Carga un proyecto primero."
    
    return book.export_to_pdf()

def refresh_all_views(project_name: str):
    """Función unificada para refrescar todas las vistas al cambiar o recargar un proyecto."""
    if not project_name:
        # Devuelve valores vacíos para todos los outputs si no hay proyecto seleccionado
        return "Selecciona un proyecto.", {}, "", ""
    return load_project(project_name)


# --- Construcción de la Interfaz de Gradio ---

with gr.Blocks(theme=gr.themes.Soft(), title="BookWriter AI") as app:
    gr.Markdown("# 📚 BookWriter AI - Tu Asistente de Escritura Local")
    
    # --- Pestaña 1: Proyectos ---
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
                choices=["Stephen King", "J.K. Rowling", "George R.R. Martin", "Gabriel García Márquez", "Agatha Christie", "Isaac Asimov", "Jane Austen", "Ernest Hemingway", "Neil Gaiman", "Brandon Sanderson", "Ursula K. Le Guin"],
                value="Stephen King",
                label="Inspirado en el Estilo de"
            )

        premise = gr.Textbox(label="Premisa / Sinopsis de la Historia", lines=3)
        with gr.Row():
            num_chapters = gr.Slider(3, 50, 15, step=1, label="Número de Capítulos")
            themes = gr.Textbox(label="Temas Principales (separados por comas)", placeholder="ej. soledad, descubrimiento, supervivencia")

        create_btn = gr.Button("Crear y Generar Outline", variant="primary")
        status_create = gr.Textbox(label="Estado de Creación", interactive=False)

    # --- Pestaña 2: Escritura ---
    with gr.Tab("✍️ Escritura y Exportación"):
        status_display = gr.Textbox(label="Estado del Proyecto", lines=8, interactive=False)
        
        with gr.Row():
            gen_page_btn = gr.Button("📄 Generar Siguiente Página", variant="primary", scale=2)
            export_btn = gr.Button("📥 Exportar a PDF", variant="secondary", scale=1)

        last_page = gr.Textbox(label="Última Página Generada", lines=15, interactive=False)
        export_status = gr.Textbox(label="Estado de Exportación", interactive=False)

    # --- Pestaña 3: Manuscrito ---
    with gr.Tab("📖 Manuscrito Completo"):
        book_display = gr.Markdown("Carga un proyecto para ver el contenido del manuscrito.")
        refresh_book_btn = gr.Button("🔄 Actualizar Vista del Manuscrito")

    # --- Pestaña 4: Memoria ---
    with gr.Tab("🧠 Memoria del Proyecto"):
        memory_display = gr.JSON(label="Memoria Completa del Proyecto (Outline, Personajes, etc.)")
        refresh_memory_btn = gr.Button("🔄 Actualizar Vista de la Memoria")

    # --- Conexiones de Eventos de la Interfaz ---
    
    # Al cargar la app, llena la lista de proyectos.
    app.load(get_project_list, outputs=project_select)

    # Botón para crear un proyecto
    create_btn.click(
        fn=create_project,
        inputs=[new_name, premise, num_chapters, themes, author_style],
        outputs=[status_create, project_select]
    )

    # Botones para cargar o refrescar vistas
    load_btn.click(
        fn=refresh_all_views,
        inputs=[project_select],
        outputs=[status_display, memory_display, book_display, last_page]
    )
    refresh_book_btn.click(
        fn=refresh_all_views,
        inputs=[project_select],
        outputs=[status_display, memory_display, book_display, last_page]
    )
    refresh_memory_btn.click(
        fn=refresh_all_views,
        inputs=[project_select],
        outputs=[status_display, memory_display, book_display, last_page]
    )
    
    # El dropdown de selección de proyecto también refresca todo
    project_select.change(
        fn=refresh_all_views,
        inputs=[project_select],
        outputs=[status_display, memory_display, book_display, last_page]
    )

    # Botón principal para generar una página
    gen_page_btn.click(
        fn=generate_next_page,
        outputs=[status_create, status_display, book_display, last_page, memory_display]
    )
    
    # Botón para exportar a PDF
    export_btn.click(export_pdf, outputs=[export_status])

# --- Lanzar la Aplicación ---
if __name__ == "__main__":
    app.launch()


