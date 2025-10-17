import gradio as gr
from bookwriter.core import BookWriter
from bookwriter.config import PROJECTS_PATH
from bookwriter.styles import STYLE_PRESETS
from bookwriter.validators import InputValidator
import os
import time
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Estado Global ---
active_project_state = {"book": None}

# --- Funciones de Utilidad ---
def get_project_list():
    """Obtiene y devuelve la lista de proyectos existentes."""
    if not PROJECTS_PATH.exists():
        PROJECTS_PATH.mkdir()
    return [d.name for d in PROJECTS_PATH.iterdir() if d.is_dir()]

def get_style_profile_choices():
    """Obtiene las opciones de perfiles de estilo con descripciones."""
    choices = []
    for profile_key, profile_data in STYLE_PRESETS.items():
        label = f"{profile_data['name']}"
        choices.append((label, profile_key))
    return choices

def update_status_display(status_dict: dict) -> str:
    """Formatea el diccionario de estado en un string legible para la UI."""
    if "message" in status_dict:
        return status_dict["message"]
    
    ollama_icon = "🟢" if status_dict.get("ollama_status") else "🔴"
    
    # Obtener información del perfil de estilo
    style_profile = status_dict.get('style_profile', 'balanced_neutral')
    profile_name = STYLE_PRESETS.get(style_profile, {}).get('name', style_profile)
    
    if status_dict.get('completed'):
        return f"""📖 **{status_dict['title']}**
---
✅ **LIBRO COMPLETADO**
---
✏️ Estilo de Autor: {status_dict['style']}
🎨 Perfil Narrativo: {profile_name}
📚 Total Capítulos: {status_dict['total_chapters']}
🧠 Memoria a Largo Plazo (Ollama): {ollama_icon}"""
    
    return f"""📖 **{status_dict['title']}**
---
**Progreso Actual:**
- **Capítulo {status_dict['current_chapter_number']}:** "{status_dict['current_chapter_title']}"
- **Página:** {status_dict['current_page']} / {status_dict['pages_in_chapter']}
---
✏️ Estilo de Autor: {status_dict['style']}
🎨 Perfil Narrativo: {profile_name}
📚 Total Capítulos: {status_dict['total_chapters']}
🧠 Memoria a Largo Plazo (Ollama): {ollama_icon}"""

def get_style_profile_description(profile_key: str) -> str:
    """Obtiene la descripción detallada de un perfil de estilo."""
    if not profile_key or profile_key not in STYLE_PRESETS:
        return "Selecciona un perfil para ver su descripción."
    
    profile = STYLE_PRESETS[profile_key]
    
    description = f"""### 📖 {profile['name']}

**Descripción:**
{profile['description']}

**Características Principales:**
"""
    
    # Añadir dimensiones
    dimensions = profile.get('dimensions', {})
    dimension_labels = {
        'prose_complexity': '✍️ Complejidad de Prosa',
        'narrative_density': '📊 Densidad Narrativa',
        'description_level': '🎨 Nivel de Descripción',
        'thematic_depth': '🧠 Profundidad Temática',
        'dialogue_style': '💬 Estilo de Diálogo'
    }
    
    for dim_key, level in dimensions.items():
        label = dimension_labels.get(dim_key, dim_key)
        description += f"\n- **{label}:** {level.replace('_', ' ').title()}"
    
    # Añadir instrucciones especiales si existen
    special_instructions = profile.get('special_instructions', [])
    if special_instructions and len(special_instructions) > 0:
        description += "\n\n**Instrucciones Especiales:**"
        for instruction in special_instructions[:5]:  # Mostrar máximo 5
            description += f"\n- {instruction}"
    
    return description

# --- Funciones de Lógica de la Interfaz ---
def load_project(project_name: str):
    """Carga un proyecto y actualiza todos los componentes de la UI."""
    # Manejar el caso en que el input es una lista
    if isinstance(project_name, list) and project_name:
        project_name = project_name[0]
        
    if not project_name:
        return (
            "Selecciona un proyecto.", 
            {}, 
            "", 
            "", 
            "", 
            "", 
            None, 
            gr.update(choices=get_project_list()),
            ""  # style_info
        )
    
    logger.info(f"Cargando proyecto: {project_name}...")
    
    try:
        # Crear instancia de BookWriter (cargará la memoria existente)
        book = BookWriter(project_name)
        active_project_state["book"] = book
        
        # Obtener estado
        status_dict = book.get_status()
        status_text = update_status_display(status_dict)
        
        # Leer manuscrito
        manuscript_content = ""
        if book.book_file.exists():
            manuscript_content = book.book_file.read_text(encoding='utf-8')
        
        # Obtener blurb y cover prompt
        blurb = status_dict.get('blurb', 'Aún no se ha generado un resumen.')
        cover_prompt = status_dict.get('cover_prompt', 'Aún no se ha generado un prompt para la portada.')
        cover_image = status_dict.get('cover_path')
        
        # Obtener información del perfil de estilo
        style_profile = status_dict.get('style_profile', 'balanced_neutral')
        style_info = get_style_profile_description(style_profile)
        
        logger.info(f"✅ Proyecto '{project_name}' cargado exitosamente")
        
        return (
            status_text, 
            book.memory, 
            manuscript_content, 
            "", 
            blurb, 
            cover_prompt, 
            cover_image,
            gr.update(choices=get_project_list()),
            style_info
        )
        
    except Exception as e:
        error_msg = f"❌ Error al cargar proyecto: {str(e)}"
        logger.error(error_msg)
        return (
            error_msg,
            {},
            "",
            "",
            "",
            "",
            None,
            gr.update(choices=get_project_list()),
            ""
        )

def create_project(name: str, 
                  premise: str, 
                  chapters: int, 
                  themes: str, 
                  authors: list,
                  style_profile: str,
                  progress=gr.Progress(track_tqdm=True)):
    """Crea un nuevo proyecto y genera su outline."""
    
    logger.info("=" * 60)
    logger.info("CREANDO NUEVO PROYECTO")
    logger.info("=" * 60)
    
    # Validar entradas
    is_valid, message = InputValidator.validate_project_creation(
        name=name,
        premise=premise,
        chapters=chapters,
        themes=themes,
        authors=authors
    )
    
    if not is_valid:
        logger.error(f"Validación fallida: {message}")
        return message, gr.update(choices=get_project_list()), ""
    
    try:
        progress(0, desc="Inicializando proyecto...")
        
        # Crear proyecto con perfil de estilo
        logger.info(f"Creando proyecto '{name}' con perfil '{style_profile}'")
        book = BookWriter(
            project_name=name,
            author_style=authors,
            style_profile=style_profile
        )
        active_project_state["book"] = book
        
        progress(0.3, desc="Generando outline con IA...")
        
        # Generar outline
        result = book.generate_outline(premise, int(chapters), themes)
        
        progress(0.9, desc="Finalizando...")
        time.sleep(0.5)
        
        progress(1, desc="¡Outline generado!")
        
        project_list = get_project_list()
        style_info = get_style_profile_description(style_profile)
        
        logger.info(f"✅ Proyecto '{name}' creado exitosamente")
        
        return result, gr.update(choices=project_list, value=book.project_name), style_info
        
    except Exception as e:
        error_msg = f"❌ Error al crear proyecto: {str(e)}"
        logger.error(error_msg)
        return error_msg, gr.update(choices=get_project_list()), ""

def generate_blurb_interface(progress=gr.Progress(track_tqdm=True)):
    """Función de interfaz para generar el blurb."""
    book = active_project_state.get("book")
    if not book:
        return "Carga un proyecto primero.", {}
    
    try:
        progress(0.5, desc="Generando resumen con IA...")
        blurb = book.generate_book_blurb()
        progress(1, desc="¡Resumen generado!")
        return blurb, book.memory
    except Exception as e:
        error_msg = f"❌ Error al generar blurb: {str(e)}"
        logger.error(error_msg)
        return error_msg, {}

def generate_cover_interface(progress=gr.Progress(track_tqdm=True)):
    """Función de interfaz para generar la portada."""
    book = active_project_state.get("book")
    if not book:
        return None, "Carga un proyecto primero.", "", {}
    
    try:
        progress(0, desc="Paso 1/2: Creando prompt artístico...")
        image_path, cover_prompt, status = book.generate_cover_art()
        
        if image_path:
            progress(1, desc="Paso 2/2: ¡Portada generada!")
        else:
            progress(1, desc="Error al generar portada.")
        
        return image_path, cover_prompt, status, book.memory
        
    except Exception as e:
        error_msg = f"❌ Error al generar portada: {str(e)}"
        logger.error(error_msg)
        return None, "", error_msg, {}

def write_full_book_interface(progress=gr.Progress(track_tqdm=True)):
    """Función de interfaz para escribir el libro completo."""
    book = active_project_state.get("book")
    if not book:
        yield "Carga un proyecto primero.", gr.update(), gr.update(), gr.update(), gr.update(), gr.update()
        return
    
    try:
        for percentage, message in book.write_full_book():
            progress(percentage, desc=message)
            yield message, gr.update(), gr.update(), gr.update(), gr.update(), gr.update()
            
    except Exception as e:
        error_msg = f"❌ Error durante la escritura del libro: {str(e)}"
        logger.error(error_msg)
        yield error_msg, gr.update(), gr.update(), gr.update(), gr.update(), gr.update()
        return
    
    logger.info("Refrescando la interfaz tras la escritura completa.")
    
    # Actualizar vistas finales
    final_status_dict = book.get_status()
    final_status_text = update_status_display(final_status_dict)
    
    final_manuscript = ""
    if book.book_file.exists():
        final_manuscript = book.book_file.read_text(encoding='utf-8')
    
    yield (
        "✅ ¡Proceso de escritura finalizado!",
        final_status_text,
        final_manuscript,
        "",
        book.memory,
        gr.update(choices=get_project_list(), value=book.project_name)
    )

def generate_next_page():
    """Genera la siguiente página del libro."""
    book = active_project_state.get("book")
    if not book:
        return "Carga un proyecto primero.", "", "", "", {}
    
    try:
        status_update, page_content = book.generate_page()
        
        # Leer manuscrito actualizado
        manuscript_content = ""
        if book.book_file.exists():
            manuscript_content = book.book_file.read_text(encoding='utf-8')
        
        # Obtener estado actualizado
        status_dict = book.get_status()
        status_text = update_status_display(status_dict)
        
        return status_update, status_text, manuscript_content, page_content, book.memory
        
    except Exception as e:
        error_msg = f"❌ Error al generar página: {str(e)}"
        logger.error(error_msg)
        return error_msg, "", "", "", {}

def export_pdf(progress=gr.Progress(track_tqdm=True)):
    """Exporta el libro a PDF."""
    book = active_project_state.get("book")
    if not book:
        return "Carga un proyecto primero."
    
    try:
        progress(0.5, desc="Generando archivo PDF...")
        result = book.export_to_pdf()
        progress(1, desc="¡PDF Exportado!")
        return result
    except Exception as e:
        error_msg = f"❌ Error al exportar PDF: {str(e)}"
        logger.error(error_msg)
        return error_msg

def refresh_all_views(project_name: str):
    """Función unificada para refrescar todas las vistas."""
    if not project_name:
        return (
            "Selecciona un proyecto.",
            {},
            "",
            "",
            "Carga un proyecto.",
            "",
            None,
            ""
        )
    return load_project(project_name)

def update_style_description(profile_key: str):
    """Actualiza la descripción del perfil seleccionado."""
    return get_style_profile_description(profile_key)

def generate_consistency_report():
    """Genera un reporte de consistencia del proyecto actual."""
    book = active_project_state.get("book")
    if not book:
        return "Carga un proyecto primero."
    
    try:
        report = book.generate_consistency_report()
        return report
    except Exception as e:
        error_msg = f"❌ Error al generar reporte: {str(e)}"
        logger.error(error_msg)
        return error_msg

# --- Construcción de la Interfaz ---
with gr.Blocks(theme=gr.themes.Soft(), title="BookWriter AI") as app:
    
    gr.Markdown("""
    # 📚 BookWriter AI - Tu Asistente de Escritura Local
    
    ### Sistema avanzado de generación de novelas con IA
    Genera libros completos con coherencia narrativa profunda, memoria a largo plazo y estilos adaptativos.
    """)
    
    # Opciones de autores (mantenemos las existentes)
    author_choices = [
        # --- Terror / Horror ---
        ("Terror / Horror: Anne Rice", "Anne Rice"),
        ("Terror / Horror: Bram Stoker", "Bram Stoker"),
        ("Terror / Horror: Clive Barker", "Clive Barker"),
        ("Terror / Horror: Edgar Allan Poe", "Edgar Allan Poe"),
        ("Terror / Horror: H.P. Lovecraft", "H.P. Lovecraft"),
        ("Terror / Horror: Mark Z. Danielewski", "Mark Z. Danielewski"),
        ("Terror / Horror: Mary Shelley", "Mary Shelley"),
        ("Terror / Horror: Shirley Jackson", "Shirley Jackson"),
        ("Terror / Horror: Stephen King", "Stephen King"),

        # --- Ciencia Ficción ---
        ("Ciencia Ficción: Andy Weir", "Andy Weir"),
        ("Ciencia Ficción: Arthur C. Clarke", "Arthur C. Clarke"),
        ("Ciencia Ficción: Frank Herbert", "Frank Herbert"),
        ("Ciencia Ficción: Isaac Asimov", "Isaac Asimov"),
        ("Ciencia Ficción: N.K. Jemisin", "N.K. Jemisin"),
        ("Ciencia Ficción: Philip K. Dick", "Philip K. Dick"),
        ("Ciencia Ficción: Ted Chiang", "Ted Chiang"),
        ("Ciencia Ficción: Ursula K. Le Guin", "Ursula K. Le Guin"),
        ("Ciencia Ficción: William Gibson", "William Gibson"),
        
        # --- Fantasía ---
        ("Fantasía: Brandon Sanderson", "Brandon Sanderson"),
        ("Fantasía: C.S. Lewis", "C.S. Lewis"),
        ("Fantasía: George R.R. Martin", "George R.R. Martin"),
        ("Fantasía: J.K. Rowling", "J.K. Rowling"),
        ("Fantasía: J.R.R. Tolkien", "J.R.R. Tolkien"),
        ("Fantasía: Neil Gaiman", "Neil Gaiman"),
        ("Fantasía: Patrick Rothfuss", "Patrick Rothfuss"),
        ("Fantasía: Terry Pratchett", "Terry Pratchett"),

        # --- Misterio / Thriller ---
        ("Misterio / Thriller: Agatha Christie", "Agatha Christie"),
        ("Misterio / Thriller: Arthur Conan Doyle", "Arthur Conan Doyle"),
        ("Misterio / Thriller: Dennis Lehane", "Dennis Lehane"),
        ("Misterio / Thriller: Gillian Flynn", "Gillian Flynn"),
        ("Misterio / Thriller: Raymond Chandler", "Raymond Chandler"),
        ("Misterio / Thriller: Tana French", "Tana French"),

        # --- Aventura ---
        ("Aventura: Alexandre Dumas", "Alexandre Dumas"),
        ("Aventura: Emilio Salgari", "Emilio Salgari"),
        ("Aventura: H.G. Wells", "H.G. Wells"),
        ("Aventura: Jack London", "Jack London"),
        ("Aventura: Jules Verne", "Jules Verne"),
        ("Aventura: Robert Louis Stevenson", "Robert Louis Stevenson"),
        
        # --- Romance ---
        ("Romance: Emily Brontë", "Emily Brontë"),
        ("Romance: Helen Fielding", "Helen Fielding"),
        ("Romance: Jane Austen", "Jane Austen"),
        ("Romance: Julia Quinn", "Julia Quinn"),
        ("Romance: Nicholas Sparks", "Nicholas Sparks"),
        ("Romance: Nora Roberts", "Nora Roberts"),

        # --- Realismo Mágico ---
        ("Realismo Mágico: Gabriel García Márquez", "Gabriel García Márquez"),
        ("Realismo Mágico: Haruki Murakami", "Haruki Murakami"),
        ("Realismo Mágico: Isabel Allende", "Isabel Allende"),
        ("Realismo Mágico: Julio Cortázar", "Julio Cortázar"),

        # --- Clásicos / Ficción Literaria ---
        ("Clásicos / Literarios: Albert Camus", "Albert Camus"),
        ("Clásicos / Literarios: Charles Dickens", "Charles Dickens"),
        ("Clásicos / Literarios: Ernest Hemingway", "Ernest Hemingway"),
        ("Clásicos / Literarios: Fiodor Dostoievski", "Fiodor Dostoievski"),
        ("Clásicos / Literarios: Herman Melville", "Herman Melville"),
        ("Clásicos / Literarios: Italo Calvino", "Italo Calvino"),
        ("Clásicos / Literarios: John Steinbeck", "John Steinbeck"),
        ("Clásicos / Literarios: Jorge Luis Borges", "Jorge Luis Borges"),
        ("Clásicos / Literarios: Joseph Conrad", "Joseph Conrad"),
        ("Clásicos / Literarios: Leo Tolstoy", "Leo Tolstoy"),
        ("Clásicos / Literarios: Mark Twain", "Mark Twain"),
        ("Clásicos / Literarios: Miguel de Cervantes", "Miguel de Cervantes"),
        ("Clásicos / Literarios: Oscar Wilde", "Oscar Wilde"),
        ("Clásicos / Literarios: Paulo Coelho", "Paulo Coelho"),
        ("Clásicos / Literarios: Victor Hugo", "Victor Hugo"),
        ("Clásicos / Literarios: Virginia Woolf", "Virginia Woolf"),
        ("Clásicos / Literarios: Walt Whitman", "Walt Whitman"),

        # --- Ensayo / No Ficción ---
        ("Filosofía / Ensayo: Friedrich Nietzsche", "Friedrich Nietzsche"),
        ("Filosofía / Ensayo: Simone de Beauvoir", "Simone de Beauvoir"),
        ("Filosofía / Ensayo: Yuval Noah Harari", "Yuval Noah Harari"),
        ("Psicología / Autoayuda: Brené Brown", "Brené Brown"),
        ("Psicología / Autoayuda: Carl Jung", "Carl Jung"),
        ("Psicología / Autoayuda: Jordan Peterson", "Jordan Peterson"),
        ("Psicología / Autoayuda: Mark Manson", "Mark Manson"),
    ]

    with gr.Tab("🚀 Gestión de Proyectos"):
        gr.Markdown("### Cargar un Proyecto Existente")
        with gr.Row():
            project_select = gr.Dropdown(
                choices=get_project_list(), 
                label="Proyectos Guardados", 
                interactive=True
            )
            load_btn = gr.Button("Cargar Proyecto", variant="secondary")
        
        gr.Markdown("---")
        
        gr.Markdown("### Crear un Nuevo Proyecto")
        
        with gr.Row():
            new_name = gr.Textbox(
                label="Título del Libro",
                placeholder="Ej: El Protocolo Genesis"
            )
            author_style = gr.Dropdown(
                label="Inspirado en el Estilo de (elige uno o más)",
                choices=author_choices,
                multiselect=True,
                interactive=True
            )
        
        premise = gr.Textbox(
            label="Premisa / Sinopsis", 
            lines=3,
            placeholder="Describe la idea central de tu historia..."
        )
        
        with gr.Row():
            num_chapters = gr.Slider(
                3, 50, 15, 
                step=1, 
                label="Número de Capítulos"
            )
            themes = gr.Textbox(
                label="Temas (separados por comas)", 
                placeholder="ej. soledad, supervivencia, identidad"
            )
        
        # NUEVO: Selector de perfil de estilo
        gr.Markdown("### 🎨 Configuración de Estilo Narrativo")
        
        style_profile_selector = gr.Dropdown(
            label="Perfil de Estilo",
            choices=get_style_profile_choices(),
            value="balanced_neutral",
            interactive=True
        )
        
        style_profile_info = gr.Markdown(
            get_style_profile_description("balanced_neutral")
        )
        
        # Actualizar descripción cuando cambie la selección
        style_profile_selector.change(
            fn=update_style_description,
            inputs=[style_profile_selector],
            outputs=[style_profile_info]
        )
        
        create_btn = gr.Button("Crear y Generar Outline", variant="primary", size="lg")
        status_create = gr.Textbox(label="Estado de Creación", interactive=False)
        
    with gr.Tab("✏️ Escritura y Exportación"):
        status_display = gr.Textbox(
            label="Estado del Proyecto", 
            lines=10, 
            interactive=False
        )
        
        with gr.Row():
            gen_page_btn = gr.Button(
                "📄 Generar Página Siguiente", 
                variant="secondary", 
                scale=1
            )
            write_full_book_btn = gr.Button(
                "📚 Escribir Libro Completo", 
                variant="primary", 
                scale=2
            )
            export_btn = gr.Button(
                "📥 Exportar a PDF", 
                variant="secondary", 
                scale=1
            )
            
        last_page = gr.Textbox(
            label="Última Página Generada", 
            lines=15, 
            interactive=False
        )
        export_status = gr.Textbox(label="Estado de Exportación", interactive=False)
        
        gr.Markdown("---")
        gr.Markdown("### Resumen y Portada")
        
        with gr.Row():
            with gr.Column(scale=2):
                blurb_display = gr.Textbox(
                    label="Resumen de Contraportada", 
                    lines=7, 
                    interactive=False
                )
                gen_blurb_btn = gr.Button(
                    "✨ Generar / Regenerar Resumen", 
                    variant="secondary"
                )
                
                cover_prompt_display = gr.Textbox(
                    label="Prompt Artístico para Portada", 
                    lines=4, 
                    interactive=False
                )
                gen_cover_btn = gr.Button(
                    "🎨 Generar Portada con IA", 
                    variant="primary"
                )
                cover_status = gr.Textbox(label="Estado de la Portada", interactive=False)
                
            with gr.Column(scale=1):
                cover_image_display = gr.Image(
                    label="Portada Generada", 
                    type="filepath", 
                    interactive=False
                )

    with gr.Tab("📖 Manuscrito Completo"):
        book_display = gr.Textbox(
            label="Manuscrito",
            value="Carga un proyecto para ver el manuscrito.",
            lines=30,
            interactive=False,
            show_copy_button=True
        )
        refresh_book_btn = gr.Button("🔄 Actualizar Vista")
        
    with gr.Tab("🧠 Memoria del Proyecto"):
        memory_display = gr.JSON(label="Memoria Completa del Proyecto")
        refresh_memory_btn = gr.Button("🔄 Actualizar Vista")
    
    with gr.Tab("🎨 Información de Estilo"):
        gr.Markdown("""
        ### Perfil de Estilo Activo
        
        Esta sección muestra el perfil de estilo configurado para el proyecto actual.
        """)
        
        style_info_display = gr.Markdown(
            "Carga un proyecto para ver su configuración de estilo."
        )
        
        gr.Markdown("---")
        gr.Markdown("### 📊 Reporte de Consistencia")
        
        consistency_report_display = gr.Textbox(
            label="Reporte de Consistencia Narrativa",
            lines=20,
            interactive=False
        )
        
        generate_report_btn = gr.Button(
            "📊 Generar Reporte de Consistencia",
            variant="secondary"
        )

    # --- Conexiones de Eventos ---
    
    # Outputs estándar al cargar proyecto
    outputs_on_load = [
        status_display,
        memory_display,
        book_display,
        last_page,
        blurb_display,
        cover_prompt_display,
        cover_image_display,
        project_select,
        style_info_display
    ]
    
    # Cargar lista de proyectos al iniciar
    app.load(get_project_list, outputs=project_select)
    
    # Crear proyecto
    create_btn.click(
        fn=create_project,
        inputs=[
            new_name,
            premise,
            num_chapters,
            themes,
            author_style,
            style_profile_selector
        ],
        outputs=[status_create, project_select, style_info_display]
    )
    
    # Cargar proyecto
    load_btn.click(
        fn=refresh_all_views,
        inputs=[project_select],
        outputs=outputs_on_load
    )
    
    # Cambio en selector de proyecto
    project_select.change(
        fn=refresh_all_views,
        inputs=[project_select],
        outputs=outputs_on_load
    )
    
    # Refrescar vistas
    refresh_book_btn.click(
        fn=refresh_all_views,
        inputs=[project_select],
        outputs=outputs_on_load
    )
    
    refresh_memory_btn.click(
        fn=refresh_all_views,
        inputs=[project_select],
        outputs=outputs_on_load
    )
    
    # Generar página
    gen_page_btn.click(
        fn=generate_next_page,
        outputs=[
            status_create,
            status_display,
            book_display,
            last_page,
            memory_display
        ]
    )
    
    # Generar blurb
    gen_blurb_btn.click(
        fn=generate_blurb_interface,
        outputs=[blurb_display, memory_display]
    )
    
    # Generar portada
    gen_cover_btn.click(
        fn=generate_cover_interface,
        outputs=[
            cover_image_display,
            cover_prompt_display,
            cover_status,
            memory_display
        ]
    )
    
    # Escribir libro completo
    write_full_book_btn.click(
        fn=write_full_book_interface,
        outputs=[
            status_create,
            status_display,
            book_display,
            last_page,
            memory_display,
            project_select
        ]
    )
    
    # Exportar PDF
    export_btn.click(
        fn=export_pdf,
        outputs=[export_status]
    )
    
    # Generar reporte de consistencia
    generate_report_btn.click(
        fn=generate_consistency_report,
        outputs=[consistency_report_display]
    )

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("INICIANDO BOOKWRITER AI")
    logger.info("=" * 60)
    
    app.launch(
        server_name="0.0.0.0",  # Permitir acceso desde la red local
        server_port=7860,
        share=False  # Cambiar a True si quieres compartir públicamente
    )