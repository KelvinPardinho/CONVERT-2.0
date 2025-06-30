# services/protect_pdf.py (VERSÃO CORRIGIDA)

import os
import fitz  # PyMuPDF
from typing import Tuple

def process_protect_pdf(
    pdf_file_bytes: bytes,
    password: str,
    output_dir: str,
    base_filename: str
) -> Tuple[bool, str, str, dict]: # Ajustado para retornar 4 elementos
    """
    Aplica criptografia com senha a um arquivo PDF.
    """
    try:
        doc = fitz.open(stream=pdf_file_bytes, filetype="pdf")

        output_filename = f"{base_filename}_protected.pdf"
        output_path = os.path.join(output_dir, output_filename)

        # <<< CORREÇÃO AQUI >>>
        # Usando as constantes corretas da biblioteca PyMuPDF
        permissions = int(
            fitz.PDF_PERM_PRINT    # Permite imprimir
            | fitz.PDF_PERM_COPY   # Permite copiar
            | fitz.PDF_PERM_ANNOTATE # Permite adicionar anotações
        )
        
        # Usando a constante de criptografia correta
        encryption_method = fitz.PDF_ENCRYPT_AES_256

        # Salva o documento com as constantes corrigidas
        doc.save(
            output_path,
            encryption=encryption_method,
            user_pw=password,
            owner_pw=password,
            permissions=permissions,
            garbage=4,
            deflate=True
        )
        doc.close()

        # Retorna o quarto valor como None, pois não há dados extras
        return True, "PDF protegido com senha com sucesso!", output_filename, None

    except Exception as e:
        return False, f"Ocorreu um erro ao proteger o PDF: {str(e)}", "", None