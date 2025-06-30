# services/compress_pdf.py

import os
import fitz  # PyMuPDF
from typing import Tuple

def _format_bytes(size: int) -> str:
    """Formata bytes em uma string legível (KB, MB)."""
    if size < 1024:
        return f"{size} Bytes"
    elif size < 1024**2:
        return f"{size/1024:.2f} KB"
    else:
        return f"{size/1024**2:.2f} MB"

def process_compress_pdf(
    pdf_file_bytes: bytes,
    output_dir: str,
    base_filename: str,
    compression_level: str = 'medium' # Placeholder para futuras melhorias
) -> Tuple[bool, str, str, str, str, str]:
    """
    Comprime um arquivo PDF usando as opções de otimização do PyMuPDF.

    Args:
        pdf_file_bytes (bytes): O conteúdo do PDF original.
        output_dir (str): Diretório para salvar o arquivo comprimido.
        base_filename (str): Nome do arquivo original sem extensão.
        compression_level (str): Nível de compressão desejado ('low', 'medium', 'high').

    Returns:
        Tuple: (success, message, output_filename, original_size, compressed_size, ratio)
    """
    try:
        original_size = len(pdf_file_bytes)
        
        # Abre o PDF a partir dos bytes em memória
        doc = fitz.open(stream=pdf_file_bytes, filetype="pdf")

        output_filename = f"{base_filename}_compressed.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        # As opções de salvamento do PyMuPDF são a chave para a compressão.
        # garbage=4: remove objetos não utilizados de forma agressiva.
        # deflate=True: comprime os fluxos de dados.
        # clean=True: limpa e embeleza a sintaxe do PDF.
        # Atualmente, todos os níveis usam a mesma compressão forte.
        # Níveis diferentes poderiam, no futuro, ajustar a qualidade das imagens.
        doc.save(output_path, garbage=4, deflate=True, clean=True)
        doc.close()

        compressed_size = os.path.getsize(output_path)

        if original_size > 0:
            ratio = 100 * (1 - (compressed_size / original_size))
        else:
            ratio = 0
            
        return (
            True,
            "PDF comprimido com sucesso!",
            output_filename,
            _format_bytes(original_size),
            _format_bytes(compressed_size),
            f"{ratio:.2f}%"
        )

    except Exception as e:
        return (False, f"Ocorreu um erro ao comprimir o PDF: {str(e)}", "", "", "", "")