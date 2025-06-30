# services/split_pdf.py

import os
import io
import zipfile
from typing import List, Tuple, Any
from PyPDF2 import PdfReader, PdfWriter

def process_split_pdf(
    pdf_file_bytes: bytes,
    split_mode: str,
    selections: List[bool],
    rotations: List[int],
    output_dir: str,
    base_filename: str
) -> Tuple[bool, str, str]:
    """
    Processa a divisão de um arquivo PDF com base nas seleções e rotações fornecidas.

    Args:
        pdf_file_bytes (bytes): O conteúdo do arquivo PDF em bytes.
        split_mode (str): O modo de divisão ('individual' ou 'merge').
        selections (List[bool]): Uma lista de booleanos indicando quais páginas selecionar.
        rotations (List[int]): Uma lista de ângulos de rotação (0, 90, 180, 270) para cada página.
        output_dir (str): O caminho do diretório para salvar os arquivos de saída.
        base_filename (str): O nome do arquivo original sem a extensão.

    Returns:
        Tuple[bool, str, str]: Uma tupla contendo:
            - success (bool): True se a operação foi bem-sucedida, False caso contrário.
            - message (str): Uma mensagem descritiva do resultado.
            - output_filename (str): O nome do arquivo de saída (PDF ou ZIP).
    """
    try:
        # 1. Identifica as páginas que o usuário selecionou
        selected_indices = [i for i, selected in enumerate(selections) if selected]
        if not selected_indices:
            return (False, "Nenhuma página foi selecionada para a operação.", "")

        # 2. Cria um leitor de PDF a partir dos bytes do arquivo enviado
        input_pdf_reader = PdfReader(io.BytesIO(pdf_file_bytes))
        
        # 3. Processo de Rotação: Cria um PDF intermediário em memória com todas as páginas rotacionadas
        rotated_writer = PdfWriter()
        for i, page in enumerate(input_pdf_reader.pages):
            # Aplica a rotação somente se for diferente de 0
            if i < len(rotations) and rotations[i] % 360 != 0:
                page.rotate(rotations[i])
            rotated_writer.add_page(page)

        # Cria um novo leitor para o PDF rotacionado que está em memória
        rotated_buffer = io.BytesIO()
        rotated_writer.write(rotated_buffer)
        rotated_buffer.seek(0)
        rotated_pdf_reader = PdfReader(rotated_buffer)

        # 4. Lógica de Divisão baseada no modo escolhido
        
        # Modo 'merge': une as páginas selecionadas em um novo PDF único
        if split_mode == 'merge':
            output_writer = PdfWriter()
            for index in selected_indices:
                output_writer.add_page(rotated_pdf_reader.pages[index])
            
            output_filename = f"{base_filename}_merged.pdf"
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, 'wb') as f:
                output_writer.write(f)

            return (True, "Páginas unidas com sucesso!", output_filename)

        # Modo 'individual': cria um .zip com um PDF para cada página selecionada
        elif split_mode == 'individual':
            zip_filename = f"{base_filename}_split.zip"
            zip_path = os.path.join(output_dir, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
                for index in selected_indices:
                    # Cria um writer temporário para a página individual
                    page_writer = PdfWriter()
                    page_writer.add_page(rotated_pdf_reader.pages[index])
                    
                    page_filename_in_zip = f"{base_filename}_page_{index + 1}.pdf"
                    
                    # Salva a página individual em um buffer em memória
                    page_buffer = io.BytesIO()
                    page_writer.write(page_buffer)
                    page_buffer.seek(0)
                    
                    # Adiciona o conteúdo do buffer ao arquivo zip
                    zipf.writestr(page_filename_in_zip, page_buffer.getvalue())

            return (True, "Páginas divididas com sucesso!", zip_filename)
        
        else:
            return (False, "Modo de divisão inválido.", "")

    except Exception as e:
        # Captura qualquer erro durante o processo
        return (False, f"Ocorreu um erro inesperado: {str(e)}", "")