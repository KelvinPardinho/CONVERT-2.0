import os
import uuid
import fitz  # PyMuPDF
from typing import Tuple

def process_unlock_pdf(
    pdf_file_bytes: bytes,
    password: str,
    output_dir: str,
    base_filename: str
) -> Tuple[bool, str, str, dict]:
    """
    Remove a criptografia de um arquivo PDF usando a senha fornecida.

    Args:
        pdf_file_bytes (bytes): O conteúdo do PDF protegido.
        password (str): A senha para desbloquear o PDF.
        output_dir (str): Diretório para salvar o arquivo desbloqueado.
        base_filename (str): Nome do arquivo original sem extensão.

    Returns:
        Tuple[bool, str, str, dict]: (sucesso, mensagem, nome_do_arquivo_de_saida, dados_extras)
    """
    try:
        # Abre o PDF a partir dos bytes em memória
        doc = fitz.open(stream=pdf_file_bytes, filetype="pdf")

        # Verifica se o documento está realmente criptografado
        if not doc.is_encrypted:
            doc.close()
            return False, "Este PDF não está protegido por senha.", "", None

        # Tenta autenticar (desbloquear) o PDF com a senha fornecida
        # O método authenticate() retorna o número de permissões concedidas.
        # Se a senha estiver errada, ele retornará 0 ou levantará uma exceção.
        if not doc.authenticate(password):
            doc.close()
            return False, "Senha incorreta. Não foi possível remover a proteção.", "", None
            
        # Se a autenticação for bem-sucedida, o documento está desbloqueado em memória.
        # Agora, salvamos uma nova cópia sem criptografia.
        output_filename = f"{base_filename}_unlocked.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        # Salva o arquivo sem nenhuma opção de criptografia
        doc.save(output_path, garbage=4, deflate=True)
        doc.close()

        return True, "Senha removida e PDF salvo com sucesso!", output_filename, None

    except Exception as e:
        return False, f"Ocorreu um erro ao desbloquear o PDF: {str(e)}", "", None