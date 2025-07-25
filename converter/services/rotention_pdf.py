import io
import os
import uuid
from PyPDF2 import PdfReader, PdfWriter
from django.conf import settings

# Assumindo que você tem uma função como esta para obter o diretório de saída
def get_converted_dir():
    converted_dir = os.path.join(settings.MEDIA_ROOT, 'converted')
    os.makedirs(converted_dir, exist_ok=True)
    return converted_dir

# ==========================================================
# SERVICE CORRIGIDO COM LÓGICA DE ROTAÇÃO SIMPLIFICADA E CORRETA
# ==========================================================
def process_rotate_pdf(pdf_bytes, rotations, original_filename):
    """
    Roda as páginas de um PDF para ângulos específicos e salva o resultado.

    Args:
        pdf_bytes (bytes): O conteúdo do ficheiro PDF original.
        rotations (List[int]): Lista de ângulos de rotação FINAIS para cada página (0, 90, 180, 270).
        original_filename (str): O nome do ficheiro original para manter.

    Returns:
        Tuple[bool, str, str]: (sucesso, mensagem, nome_do_arquivo_final)
    """
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        writer = PdfWriter()

        for i, page in enumerate(reader.pages):
            
            # Obtém o ângulo de rotação final desejado pelo utilizador
            target_rotation = rotations[i] if i < len(rotations) else 0

            # ==========================================================
            # CORREÇÃO DEFINITIVA: Aplica a rotação final diretamente.
            # O objeto 'page' do 'reader' está sempre no seu estado original.
            # Não são necessários cálculos complexos.
            # ==========================================================
            if target_rotation > 0:
                page.rotate(target_rotation)
            
            writer.add_page(page)

        # Salva o resultado num buffer em memória
        output_buffer = io.BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)
        
        # Mantém o nome do ficheiro original
        base_name, _ = os.path.splitext(original_filename)
        output_filename = f"{base_name}_rotated.pdf"
        output_path = os.path.join(get_converted_dir(), output_filename)

        # Salva o ficheiro no disco
        with open(output_path, 'wb') as f:
            f.write(output_buffer.read())

        return True, "Ficheiro rodado com sucesso.", output_filename
    except Exception as e:
        # Fornece mais detalhes no erro para facilitar a depuração
        return False, f"Ocorreu um erro ao rodar o PDF: {type(e).__name__} - {str(e)}", None