import io
import os
import uuid
import fitz  # PyMuPDF é a melhor ferramenta para ambas as tarefas
from django.conf import settings

def get_converted_dir():
    converted_dir = os.path.join(settings.MEDIA_ROOT, 'converted')
    os.makedirs(converted_dir, exist_ok=True)
    return converted_dir

def process_add_page_numbers(pdf_bytes, position, start_from, rotation, output_dir, original_filename):
    """
    Primeiro, roda o PDF. Depois, adiciona os números de página.
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        # PASSO 1: Rodar todas as páginas (se necessário)
        if rotation > 0:
            for page in doc:
                page.set_rotation(rotation)

        # PASSO 2: Adicionar os números de página (lógica que já funciona)
        current_page_number_to_display = 1
        for i, page in enumerate(doc):
            page_index = i + 1
            if page_index >= start_from:
                text = str(current_page_number_to_display)
                font = fitz.Font("helv")
                text_width = font.text_length(text, fontsize=11)
                page_width = page.rect.width
                page_height = page.rect.height

                if position == 'bottom-center':
                    point = fitz.Point((page_width - text_width) / 2, page_height - 30)
                elif position == 'bottom-right':
                    point = fitz.Point(page_width - text_width - 50, page_height - 30)
                elif position == 'top-center':
                    point = fitz.Point((page_width - text_width) / 2, 50)
                elif position == 'top-right':
                    point = fitz.Point(page_width - text_width - 50, 50)
                
                page.insert_text(point, text, fontsize=11, fontname="helv", color=(0, 0, 0))
                current_page_number_to_display += 1

        output_buffer = doc.write()
        doc.close()
        
        base_name, _ = os.path.splitext(original_filename)
        output_filename = f"{base_name}_numbered.pdf"
        output_path = os.path.join(output_dir, output_filename)

        with open(output_path, 'wb') as f:
            f.write(output_buffer)

        return True, "Números de página adicionados com sucesso.", output_filename
    except Exception as e:
        return False, f"Ocorreu um erro: {str(e)}", None