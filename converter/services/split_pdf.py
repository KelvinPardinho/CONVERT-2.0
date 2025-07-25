import os
import io
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
        
        # Primeiro, aplica todas as rotações necessárias em um PDF temporário em memória
        rotated_writer = PdfWriter()
        for i, page in enumerate(input_pdf_reader.pages):
            if i < len(rotations) and rotations[i] != 0:
                page.rotate(rotations[i])
            rotated_writer.add_page(page)
        
        # Cria um novo leitor a partir do PDF rotacionado em memória
        rotated_buffer = io.BytesIO()
        rotated_writer.write(rotated_buffer)
        rotated_buffer.seek(0)
        rotated_pdf_reader = PdfReader(rotated_buffer)

        selected_indices = [i for i, selected in enumerate(selections) if selected]

        # --- LÓGICA PARA CADA MODO DE DIVISÃO ---

        if split_mode == 'merge':
            # Une todas as páginas selecionadas em um único arquivo PDF
            if not selected_indices:
                return (False, "Nenhuma página foi selecionada.", "", {})
            
            output_writer = PdfWriter()
            for index in selected_indices:
                if 0 <= index < num_pages:
                    output_writer.add_page(rotated_pdf_reader.pages[index])
            
            output_filename = f"{base_filename}_merged.pdf"
            output_path = os.path.join(output_dir, output_filename)
            with open(output_path, 'wb') as f:
                output_writer.write(f)
            
            return True, "Páginas unidas com sucesso!", output_filename, {}

        elif split_mode == 'individual':
            # Cria um arquivo .zip contendo cada página selecionada como um PDF separado
            if not selected_indices:
                return (False, "Nenhuma página foi selecionada.", "", {})

            zip_filename = f"{base_filename}_split.zip"
            zip_path = os.path.join(output_dir, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
                for index in selected_indices:
                    if 0 <= index < num_pages:
                        page_writer = PdfWriter()
                        page_writer.add_page(rotated_pdf_reader.pages[index])
                        
                        page_buffer = io.BytesIO()
                        page_writer.write(page_buffer)
                        page_buffer.seek(0)
                        
                        page_name_in_zip = f"{base_filename}_page_{index + 1}.pdf"
                        zipf.writestr(page_name_in_zip, page_buffer.getvalue())

            return True, "Páginas extraídas com sucesso!", zip_filename, {}

        elif split_mode == 'pairs':
            # Divide o PDF em arquivos contendo duas páginas cada
            if num_pages < 2:
                return (False, "O PDF precisa ter pelo menos 2 páginas para ser dividido em pares.", "", {})

            zip_filename = f"{base_filename}_pairs.zip"
            zip_path = os.path.join(output_dir, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
                for i in range(0, num_pages, 2):
                    page_writer = PdfWriter()
                    page_writer.add_page(rotated_pdf_reader.pages[i])
                    
                    if (i + 1) < num_pages:
                        page_writer.add_page(rotated_pdf_reader.pages[i + 1])
                        page_name_in_zip = f"{base_filename}_pages_{i+1}-{i+2}.pdf"
                    else:
                        page_name_in_zip = f"{base_filename}_page_{i+1}.pdf"

                    page_buffer = io.BytesIO()
                    page_writer.write(page_buffer)
                    page_buffer.seek(0)
                    zipf.writestr(page_name_in_zip, page_buffer.getvalue())

            return True, "PDF dividido em pares com sucesso!", zip_filename, {}

        else:
            return False, f"Modo de divisão desconhecido: {split_mode}", "", {}

    except Exception as e:
        return False, f"Ocorreu um erro ao processar o PDF: {str(e)}", "", {}