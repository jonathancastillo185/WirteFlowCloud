from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus.tables import TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
import os
import markdown2

def export_book_to_pdf(pdf_path: str, book_file_path: str, memory: dict) -> str:
    """
    Exporta el manuscrito a un PDF profesional, asegurando la correcta generación
    del índice de contenidos.
    """
    if not os.path.exists(book_file_path):
        return "❌ No hay un manuscrito para exportar. Escribe algunas páginas primero."

    try:
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=2.5*cm, leftMargin=2.5*cm,
            topMargin=2.5*cm, bottomMargin=2.5*cm
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(name='CoverTitle', parent=styles['h1'], fontSize=36, alignment=TA_CENTER, spaceAfter=20)
        author_style = ParagraphStyle(name='CoverAuthor', parent=styles['Normal'], fontSize=14, alignment=TA_CENTER, spaceAfter=100, textColor=colors.grey)
        toc_title_style = ParagraphStyle(name='TOCTitle', parent=styles['h1'], fontSize=24, alignment=TA_CENTER, spaceBefore=20, spaceAfter=20)
        chapter_title_style = ParagraphStyle(name='ChapterTitle', parent=styles['h2'], fontSize=18, spaceBefore=20, spaceAfter=12, keepWithNext=1, textColor=colors.darkblue)
        body_style = ParagraphStyle(name='BodyText', parent=styles['Normal'], fontSize=11, alignment=TA_JUSTIFY, firstLineIndent=1*cm, leading=14, spaceAfter=6)
        blurb_style = ParagraphStyle(name='BlurbText', parent=body_style, fontSize=12, alignment=TA_LEFT, firstLineIndent=0, leading=16, spaceBefore=12, spaceAfter=12, leftIndent=1*cm, rightIndent=1*cm, borderColor=colors.black, borderPadding=10)
        toc_entry_style = ParagraphStyle(name='TOCEntry', parent=styles['Normal'], fontSize=12, leftIndent=1*cm, firstLineIndent=0, spaceBefore=4, spaceAfter=4)

        story = []
        metadata = memory.get('metadata', {})
        
        # 1. Portada
        cover_image_path = os.path.join(os.path.dirname(pdf_path), 'cover.png')
        if os.path.exists(cover_image_path):
            img = Image(cover_image_path, width=16*cm, height=24*cm, kind='proportional')
            img.hAlign = 'CENTER'
            story.append(img)
        else:
            story.append(Spacer(1, 5*cm))
            story.append(Paragraph(metadata.get('title', 'Sin Título'), title_style))
            story.append(Paragraph(f"Inspirado en el estilo de {metadata.get('author_style', 'Desconocido')}", author_style))
        story.append(PageBreak())

        # 2. Índice de Contenidos
        story.append(Paragraph("Índice de Contenidos", toc_title_style))
        toc = TableOfContents()
        toc.levelStyles = [toc_entry_style]
        story.append(toc)
        story.append(PageBreak())

        # 3. Cuerpo del Libro
        with open(book_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                stripped_line = line.strip()
                if not stripped_line:
                    continue

                # --- LÓGICA CORREGIDA ---
                # Ahora usamos .lstrip() para quitar los '##' y luego .strip() de nuevo
                # para eliminar cualquier espacio o carácter invisible que haya quedado.
                if stripped_line.startswith('##'):
                    title_text = stripped_line.lstrip('#').strip()
                    p_title = Paragraph(f'<a name="{title_text.replace(" ", "_")}"/>{title_text}', chapter_title_style)
                    p_title.toc_level = 0
                    story.append(p_title)
                else:
                    html_line = markdown2.markdown(stripped_line)
                    p_body = Paragraph(html_line, body_style)
                    story.append(p_body)
        
        story.append(PageBreak())
        
        # 4. Contraportada (Blurb)
        story.append(Paragraph("Resumen", toc_title_style))
        blurb_text = metadata.get('blurb', 'No se ha generado un resumen para este libro.')
        html_blurb = markdown2.markdown(blurb_text)
        story.append(Paragraph(html_blurb, blurb_style))

        # --- Generación Final del PDF ---
        doc.multiBuild(story)
        
        return f"✅ PDF exportado con éxito a: {os.path.basename(pdf_path)}"
        
    except Exception as e:
        print(f"❌ Error al exportar PDF: {e}")
        return f"❌ Error al exportar PDF: {e}"