import os
import uuid
import docx2pdf
from typing import Tuple
import platform 

if platform.system() == "Windows":
    import comtypes.client



def process_word_to_pdf(word_file, output_dir: str) -> Tuple[bool, str, str]:

    temp_input_name = f"{uuid.uuid4().hex}_{word_file.name}"
    input_path = os.path.join(output_dir, temp_input_name)

    base_filename = os.path.splitext(word_file.name)[0]
    output_filename = f"{base_filename}.pdf"
    output_path = os.path.join(output_dir, output_filename)

    is_windows = platform.system() == "Windows"
    if is_windows:
        comtypes.CoInitialize()

    try:
        # Salva o ficheiro Word temporariamente no disco
        with open(input_path, 'wb+') as f:
            for chunk in word_file.chunks():
                f.write(chunk)
        
        # Realiza a conversão
        docx2pdf.convert(input_path, output_path)

        return True, "Ficheiro Word convertido para PDF com sucesso!", output_filename

    except Exception as e:
        # Tenta fornecer uma mensagem de erro mais útil
        if "CoInitialize" in str(e) or "soffice" in str(e).lower() or "libreoffice" in str(e).lower():
            error_message = "Erro de conversão no servidor. Verifique se o LibreOffice ou Word está instalado e acessível."
        else:
            error_message = f"Ocorreu um erro ao converter o ficheiro: {str(e)}"
        return False, error_message, ""
        
    finally:
        # Garante que o ficheiro temporário seja sempre removido
        if os.path.exists(input_path):
            os.remove(input_path)
            
        # Garante que a "linha de comunicação" seja sempre fechada no Windows
        if is_windows:
            comtypes.CoUninitialize()