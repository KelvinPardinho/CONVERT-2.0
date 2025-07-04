import os
import io
import uuid
import zipfile
from typing import List, Tuple
from PyPDF2 import PdfReader, PdfWriter

def process_split_pdf(
    pdf_file: object, # << MUDANÇA: Recebe o objeto de arquivo, não os bytes
    split_mode: str,
    selections: List[bool],
    rotations: List[int],
    output_dir: str,
    base_filename: str
) -> Tuple[bool, str, str, dict]:
    try:
        # <<< MUDANÇA: Lê diretamente do objeto de arquivo >>>
        input_pdf_reader = PdfReader(pdf_file)
        
        num_pages = len(input_pdf_reader.pages)
        
        # O resto da lógica permanece o mesmo...
        rotated_writer = PdfWriter()
        for i, page in enumerate(input_pdf_reader.pages):
            if i < len(rotations) and rotations[i] != 0:
                page.rotate(rotations[i])
            rotated_writer.add_page(page)
        
        rotated_buffer = io.BytesIO()
        rotated_writer.write(rotated_buffer)
        rotated_buffer.seek(0)
        rotated_pdf_reader = PdfReader(rotated_buffer)

        selected_indices = [i for i, selected in enumerate(selections) if selected]

        if split_mode == 'merge':
            if not selected_indices: return (False, "Nenhuma página foi selecionada.", "", None)
            output_writer = PdfWriter()
            for index in selected_indices:
                output_writer.add_page(rotated_pdf_reader.pages[index])
            output_filename = f"{base_filename}_merged.pdf"
            output_path = os.path.join(output_dir, output_filename)
            with open(output_path, 'wb') as f:
                output_writer.write(f)
            return True, "Páginas unidas com sucesso!", output_filename, None

        elif split_mode == 'individual' or split_mode == 'pairs':
            zip_filename = f"{base_filename}_{split_mode}.zip"
            zip_path = os.path.join(output_dir, zip_filename)
            
            # Define o passo do loop: 1 para individual, 2 para pares
            step = 2 if split_mode == 'pairs' else 1
            indices_to_process = selected_indices if split_mode == 'individual' else range(0, num_pages)

            with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
                for i in range(0, len(indices_to_process), step):
                    page_writer = PdfWriter()
                    
                    if split_mode == 'individual':
                        index = indices_to_process[i]
                        page_writer.add_page(rotated_pdf_reader.pages[index])
                        page_name_in_zip = f"{base_filename}_page_{index + 1}.pdf"
                    else: # modo 'pairs'
                        index1 = indices_to_process[i]
                        page_writer.add_page(rotated_pdf_reader.pages[index1])
                        page_name_in_zip = f"{base_filename}_page_{index1 + 1}.pdf"
                        if (i + 1) < len(indices_to_process):
                            index2 = indices_to_process[i+1]
                            page_writer.add_page(rotated_pdf_reader.pages[index2])
                            page_name_in_zip = f"{base_filename}_pages_{index1+1}-{index2+1}.pdf"
                    
                    page_buffer = io.BytesIO()
                    page_writer.write(page_buffer)
                    page_buffer.seek(0)
                    zipf.writestr(page_name_in_zip, page_buffer.getvalue())

            return True, f"PDF dividido com sucesso no modo '{split_mode}'!", zip_filename, None
        
        return False, "Modo de divisão inválido.", "", None

    except Exception as e:
        return False, f"Ocorreu um erro ao dividir o PDF: {str(e)}", "", None