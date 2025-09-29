from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER

def export_book_to_pdf(book_writer_instance):
    """
    Exporta el contenido de un libro a un archivo PDF.

    Args:
        book_writer_instance: Una instancia de la clase BookWriter.

    Returns:
        Una cadena con el mensaje de éxito o error.
    """
    bw = book_writer_instance
    if not bw.book_file.exists():
        return "❌ No hay contenido en el archivo book.md para exportar."

    try:
        # Configurar el documento PDF
        doc = SimpleDocTemplate(
            str(bw.pdf_file),
            pagesize=A4,
            rightMargin=2.5 * cm,
            leftMargin=2.5 * cm,
            topMargin=2.5 * cm,
            bottomMargin=2.5 * cm
        )

        # Definir estilos de párrafo
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['h1'],
            fontSize=28,
            leading=34,
            alignment=TA_CENTER,
            spaceAfter=2 * cm
        )
        author_style = ParagraphStyle(
            'AuthorStyle',
            parent=styles['Normal'],
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=6 * cm
        )
        chapter_style = ParagraphStyle(
            'ChapterTitle',
            parent=styles['h2'],
            fontSize=20,
            leading=24,
            spaceBefore=1 * cm,
            spaceAfter=1 * cm
        )
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=12,
            leading=16,
            alignment=TA_JUSTIFY,
            firstLineIndent=1 * cm,
            spaceAfter=0.2 * cm
        )

        story = []

        # 1. Portada
        story.append(Paragraph(bw.memory['metadata']['title'], title_style))
        story.append(Paragraph(f"Un libro escrito al estilo de {bw.memory['metadata']['author_style']}", author_style))
        story.append(PageBreak())

        # 2. Contenido del libro
        book_content = bw.book_file.read_text(encoding='utf-8')
        paragraphs = book_content.split('\n')

        for p in paragraphs:
            p = p.strip()
            if p.startswith('## '):
                # Es un título de capítulo
                chapter_title = p.replace('## ', '').strip()
                story.append(Spacer(1, 1 * cm))
                story.append(Paragraph(chapter_title, chapter_style))
                story.append(Spacer(1, 0.5 * cm))
            elif p:
                # Es un párrafo de texto normal
                story.append(Paragraph(p, body_style))

        # Generar el PDF
        doc.build(story)
        return f"✅ PDF exportado con éxito en: {bw.pdf_file}"

    except Exception as e:
        return f"❌ Error al exportar a PDF: {e}"
