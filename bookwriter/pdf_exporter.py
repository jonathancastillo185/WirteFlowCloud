"""
Exportador de PDF mejorado con índice de contenidos funcional.
Genera PDFs profesionales con portada, índice interactivo y formato limpio.
"""

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
    Image, KeepTogether, Table, TableStyle
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import os
import re
import logging

logger = logging.getLogger(__name__)


class NumberedCanvas(canvas.Canvas):
    """Canvas personalizado para añadir números de página."""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """Añade números de página al guardar."""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        """Dibuja el número de página en la parte inferior."""
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.grey)
        page_num = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(
            A4[0] - 2*cm,
            1.5*cm,
            page_num
        )


class PDFExporter:
    """
    Clase para exportar manuscritos a PDF con formato profesional.
    """
    
    def __init__(self, pdf_path: str, book_file_path: str, memory: dict):
        """
        Inicializa el exportador de PDF.
        
        Args:
            pdf_path: Ruta donde guardar el PDF
            book_file_path: Ruta del archivo de manuscrito
            memory: Diccionario con la memoria del proyecto
        """
        self.pdf_path = pdf_path
        self.book_file_path = book_file_path
        self.memory = memory
        self.story = []
        
    def create_styles(self):
        """Crea y retorna los estilos personalizados."""
        styles = getSampleStyleSheet()
        
        # Helper para añadir o actualizar estilos
        def add_or_update_style(name, **kwargs):
            """Añade un estilo o actualiza si ya existe."""
            if name in styles:
                style = styles[name]
                for key, value in kwargs.items():
                    setattr(style, key, value)
            else:
                parent = kwargs.pop('parent', styles['Normal'])
                styles.add(ParagraphStyle(name=name, parent=parent, **kwargs))
        
        # Estilo para título de portada
        add_or_update_style(
            'CoverTitle',
            parent=styles['Heading1'],
            fontSize=42,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=20,
            spaceBefore=0,
            alignment=TA_CENTER,
            leading=50,
            fontName='Helvetica-Bold'
        )
        
        # Estilo para subtítulo de portada
        add_or_update_style(
            'CoverSubtitle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#666666'),
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        )
        
        # Estilo para autor en portada
        add_or_update_style(
            'CoverAuthor',
            parent=styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#444444'),
            spaceAfter=100,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        # Estilo para título del índice
        add_or_update_style(
            'TOCTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1a1a1a'),
            alignment=TA_CENTER,
            spaceAfter=30,
            spaceBefore=0,
            fontName='Helvetica-Bold'
        )
        
        # Estilo para entradas del índice
        add_or_update_style(
            'TOCEntry',
            parent=styles['Normal'],
            fontSize=12,
            leftIndent=0,
            firstLineIndent=0,
            spaceBefore=6,
            spaceAfter=6,
            leading=18,
            textColor=colors.HexColor('#333333'),
            fontName='Helvetica'
        )
        
        # Estilo para títulos de capítulo
        add_or_update_style(
            'ChapterTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#1a1a1a'),
            spaceBefore=40,
            spaceAfter=25,
            keepWithNext=1,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT
        )
        
        # Estilo para texto del cuerpo
        add_or_update_style(
            'BookBodyText',
            parent=styles['Normal'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            firstLineIndent=1*cm,
            leading=16,
            spaceAfter=10,
            textColor=colors.HexColor('#1a1a1a'),
            fontName='Helvetica'
        )
        
        # Estilo para blurb
        add_or_update_style(
            'BookBlurb',
            parent=styles['Normal'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            firstLineIndent=0,
            leading=16,
            spaceBefore=12,
            spaceAfter=12,
            leftIndent=1.5*cm,
            rightIndent=1.5*cm,
            textColor=colors.HexColor('#333333'),
            borderWidth=1,
            borderColor=colors.HexColor('#cccccc'),
            borderPadding=15,
            backColor=colors.HexColor('#f9f9f9')
        )
        
        return styles
    
    def add_cover_page(self, styles):
        """Añade la página de portada mejorada."""
        metadata = self.memory.get('metadata', {})
        cover_image_path = os.path.join(
            os.path.dirname(self.pdf_path), 
            'cover.png'
        )
        
        # Obtener el título ORIGINAL (sin sanitizar)
        title = metadata.get('title', 'Sin Título')
        # Limpiar guiones bajos si se colaron
        title = title.replace('_', ' ')
        
        # Intentar usar imagen de portada
        if os.path.exists(cover_image_path):
            try:
                img = Image(
                    cover_image_path, 
                    width=15*cm, 
                    height=22*cm,
                    kind='proportional'
                )
                img.hAlign = 'CENTER'
                self.story.append(Spacer(1, 1*cm))
                self.story.append(img)
                logger.info("Portada con imagen añadida al PDF")
            except Exception as e:
                logger.warning(f"No se pudo añadir imagen de portada: {e}")
                self._add_text_cover(styles, metadata, title)
        else:
            self._add_text_cover(styles, metadata, title)
        
        self.story.append(PageBreak())
    
    def _add_text_cover(self, styles, metadata, title):
        """Añade portada de texto elegante."""
        # Espaciado superior
        self.story.append(Spacer(1, 5*cm))
        
        # Título principal
        self.story.append(Paragraph(title, styles['CoverTitle']))
        self.story.append(Spacer(1, 0.5*cm))
        
        # Separador decorativo
        line = Table([['']], colWidths=[10*cm])
        line.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#cccccc')),
        ]))
        line.hAlign = 'CENTER'
        self.story.append(line)
        self.story.append(Spacer(1, 0.5*cm))
        
        # Subtítulo con perfil de estilo
        style_profile = metadata.get('style_profile', 'balanced_neutral')
        profile_display = style_profile.replace('_', ' ').title()
        subtitle = f"Una novela de {profile_display}"
        self.story.append(Paragraph(subtitle, styles['CoverSubtitle']))
        
        self.story.append(Spacer(1, 2*cm))
        
        # Autor(es)
        author_style = metadata.get('author_style', 'Varios Autores')
        author_text = f"Inspirado en el estilo de<br/><b>{author_style}</b>"
        self.story.append(Paragraph(author_text, styles['CoverAuthor']))
    
    def add_table_of_contents(self, styles):
        """Añade el índice de contenidos con formato mejorado."""
        self.story.append(Spacer(1, 2*cm))
        self.story.append(Paragraph("Índice de Contenidos", styles['TOCTitle']))
        self.story.append(Spacer(1, 1.5*cm))
        
        # Crear TOC personalizado
        toc = TableOfContents()
        
        # Estilo de entrada con puntos suspensivos
        toc_entry_style = ParagraphStyle(
            'TOCEntryCustom',
            parent=styles['TOCEntry'],
            fontSize=12,
            leading=18,
            leftIndent=20,
            fontName='Helvetica'
        )
        
        toc.levelStyles = [toc_entry_style]
        
        self.story.append(toc)
        self.story.append(PageBreak())
        
        logger.info("Índice de contenidos añadido")
    
    def parse_manuscript(self, styles):
        """Parsea el manuscrito y lo añade al PDF con notificaciones al TOC."""
        if not os.path.exists(self.book_file_path):
            logger.error(f"Manuscrito no encontrado: {self.book_file_path}")
            return False
        
        try:
            with open(self.book_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Procesar línea por línea
            lines = content.split('\n')
            chapter_count = 0
            paragraph_buffer = []
            
            for line in lines:
                stripped = line.strip()
                
                # Detectar títulos de capítulo (##)
                if stripped.startswith('##') and not stripped.startswith('###'):
                    # Escribir párrafo acumulado si existe
                    if paragraph_buffer:
                        combined = ' '.join(paragraph_buffer)
                        html_line = self._process_markdown(combined)
                        if html_line:
                            p_body = Paragraph(html_line, styles['BookBodyText'])
                            self.story.append(p_body)
                        paragraph_buffer = []
                    
                    chapter_count += 1
                    chapter_title = stripped.lstrip('#').strip()
                    
                    # Crear ancla única
                    anchor = f"chapter_{chapter_count}"
                    
                    # Crear título con ancla
                    title_text = self._escape_html(chapter_title)
                    title_html = f'<a name="{anchor}"/>{title_text}'
                    
                    p_title = Paragraph(title_html, styles['ChapterTitle'])
                    
                    # CRÍTICO: Notificar al TOC
                    p_title._bookmarkName = anchor
                    
                    self.story.append(p_title)
                    
                    logger.debug(f"Capítulo {chapter_count} añadido: {chapter_title}")
                
                # Detectar línea vacía (fin de párrafo)
                elif not stripped:
                    if paragraph_buffer:
                        combined = ' '.join(paragraph_buffer)
                        html_line = self._process_markdown(combined)
                        if html_line:
                            p_body = Paragraph(html_line, styles['BookBodyText'])
                            self.story.append(p_body)
                        paragraph_buffer = []
                
                # Línea de texto
                elif not stripped.startswith('#'):
                    paragraph_buffer.append(stripped)
            
            # Escribir último párrafo si existe
            if paragraph_buffer:
                combined = ' '.join(paragraph_buffer)
                html_line = self._process_markdown(combined)
                if html_line:
                    p_body = Paragraph(html_line, styles['BookBodyText'])
                    self.story.append(p_body)
            
            logger.info(f"Manuscrito parseado: {chapter_count} capítulos encontrados")
            return True
            
        except Exception as e:
            logger.error(f"Error al parsear manuscrito: {e}", exc_info=True)
            return False
    
    def _process_markdown(self, text: str) -> str:
        """Procesa markdown básico a HTML."""
        if not text:
            return ""
        
        # Escapar HTML primero
        text = self._escape_html(text)
        
        # Negritas **texto**
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        
        # Cursivas *texto* (solo si no es parte de **)
        text = re.sub(r'(?<!\*)\*([^\*]+?)\*(?!\*)', r'<i>\1</i>', text)
        
        # Cursivas _texto_
        text = re.sub(r'\b_(.+?)_\b', r'<i>\1</i>', text)
        
        return text
    
    def _escape_html(self, text: str) -> str:
        """Escapa caracteres especiales HTML."""
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        return text
    
    def add_back_matter(self, styles):
        """Añade contraportada con blurb."""
        metadata = self.memory.get('metadata', {})
        blurb = metadata.get('blurb', '')
        
        if blurb:
            self.story.append(PageBreak())
            self.story.append(Spacer(1, 3*cm))
            self.story.append(Paragraph("Sobre este Libro", styles['TOCTitle']))
            self.story.append(Spacer(1, 1*cm))
            
            # Procesar blurb markdown
            blurb_html = self._process_markdown(blurb)
            self.story.append(Paragraph(blurb_html, styles['BookBlurb']))
            
            logger.info("Contraportada añadida")
    
    def export(self) -> str:
        """
        Ejecuta la exportación completa.
        
        Returns:
            Mensaje de resultado
        """
        logger.info(f"Iniciando exportación a PDF: {self.pdf_path}")
        
        if not os.path.exists(self.book_file_path):
            msg = "❌ No hay un manuscrito para exportar. Escribe algunas páginas primero."
            logger.error(msg)
            return msg
        
        try:
            # Crear documento
            doc = SimpleDocTemplate(
                self.pdf_path,
                pagesize=A4,
                rightMargin=2.5*cm,
                leftMargin=2.5*cm,
                topMargin=2.5*cm,
                bottomMargin=2.5*cm,
                title=self.memory.get('metadata', {}).get('title', 'Libro').replace('_', ' '),
                author=self.memory.get('metadata', {}).get('author_style', 'Autor')
            )
            
            # Crear estilos
            styles = self.create_styles()
            
            # Construir documento
            self.add_cover_page(styles)
            self.add_table_of_contents(styles)
            
            # Parsear y añadir manuscrito
            if not self.parse_manuscript(styles):
                return "❌ Error al procesar el manuscrito."
            
            self.add_back_matter(styles)
            
            # Generar PDF con TOC funcional usando multiBuild
            logger.info("Generando PDF con índice funcional...")
            doc.multiBuild(
                self.story,
                canvasmaker=NumberedCanvas
            )
            
            filename = os.path.basename(self.pdf_path)
            msg = f"✅ PDF exportado con éxito: {filename}"
            logger.info(msg)
            return msg
            
        except Exception as e:
            msg = f"❌ Error al exportar PDF: {str(e)}"
            logger.error(msg, exc_info=True)
            return msg


def export_book_to_pdf(pdf_path: str, book_file_path: str, memory: dict) -> str:
    """
    Función principal de exportación (mantiene compatibilidad con código existente).
    
    Args:
        pdf_path: Ruta donde guardar el PDF
        book_file_path: Ruta del manuscrito
        memory: Memoria del proyecto
        
    Returns:
        Mensaje de resultado
    """
    exporter = PDFExporter(pdf_path, book_file_path, memory)
    return exporter.export()