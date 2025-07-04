import os
import io
import uuid
import zipfile
from typing import List, Tuple
from PyPDF2 import PdfReader, PdfWriter

def process_split_pdf(
    pdf_file_bytes: bytes,
    split_mode: str,
    selections: List[bool],
    rotations: List[int],
    output_dir: str,
    base_filename: str
) -> Tuple[bool, str, str, dict]:
    try:
        input_pdf_reader = PdfReader(io.BytesIO(pdf_file_bytes))
        num_pages = len(input_pdf_reader.pages)
        
        # Cria um PDF intermediário com todas as páginas já rotacionadas
        rotated_writer = PdfWriter()
        for i, page in enumerate(input_pdf_reader.pages):
            if i < len(rotations) and rotations[i] != 0:
                page.rotate(rotations[i])
            rotated_writer.add_page(page)
        
        rotated_buffer = io.BytesIO()
        rotated_writer.write(rotated_buffer)
        rotated_buffer.seek(0)
        rotated_pdf_reader = PdfReader(rotated_buffer)

        # Identifica as páginas selecionadas (para os modos 'individual' e 'merge')
        selected_indices = [i for i, selected in enumerate(selections) if selected]

        # --- Lógica baseada no modo de divisão ---

        # Modo 'merge' e 'individual' permanecem os mesmos
        if split_mode == 'merge':
            if not selected_indices: return (False, "Nenhuma página foi selecionada.", "", None)
            # ... (código existente de merge)
            pass

        elif split_mode == 'individual':
            if not selected_indices: return (False, "Nenhuma página foi selecionada.", "", None)
            # ... (código existente de individual)
            pass

        # <<< NOVA LÓGICA PARA 'DIVIDIR EM PARES' >>>
        elif split_mode == 'pairs':
            if num_pages < 2:
                return (False, "O PDF precisa ter pelo menos 2 páginas para ser dividido em pares.", "", None)

            zip_filename = f"{base_filename}_pairs.zip"
            zip_path = os.path.join(output_dir, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
                # Itera sobre as páginas de duas em duas
                for i in range(0, num_pages, 2):
                    page_writer = PdfWriter()
                    
                    # Adiciona a primeira página do par
                    page_writer.add_page(rotated_pdf_reader.pages[i])
                    
                    # Adiciona a segunda página, se ela existir
                    if (i + 1) < num_pages:
                        page_writer.add_page(rotated_pdf_reader.pages[i + 1])
                        page_name_in_zip = f"{base_filename}_pages_{i+1}-{i+2}.pdf"
                    else:
                        page_name_in_zip = f"{base_filename}_page_{i+1}.pdf"

                    # Salva o par em um buffer e adiciona ao zip
                    page_buffer = io.BytesIO()
                    page_writer.write(page_buffer)
                    page_buffer.seek(0)
                    zipf.writestr(page_name_in_zip, page_buffer.getvalue())

            return True, "PDF dividido em pares com sucesso!", zip_filename, None

    except Exception as e:
        return False, f"Ocorreu um erro ao dividir o PDF: {str(e)}", "", None