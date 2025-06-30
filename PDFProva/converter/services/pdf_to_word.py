# services/pdf_to_word.py (VERSÃO CORRIGIDA E OTIMIZADA)

import os
import uuid
from typing import Tuple
from pdf2docx import Converter
from pdf2image import convert_from_bytes # Importa a versão que lê da memória
from PIL import Image
import pytesseract
from docx import Document

def convert_pdf_to_word(
    pdf_file: object, 
    output_dir: str
) -> Tuple[bool, str, str]:
    """
    Converte um PDF para DOCX. Tenta uma conversão direta; se falhar, usa OCR.

    Args:
        pdf_file (UploadedFile): O objeto de arquivo PDF enviado.
        output_dir (str): O diretório para salvar o arquivo DOCX convertido.

    Returns:
        Tuple[bool, str, str]: (sucesso, nome_do_arquivo_convertido, mensagem_de_erro)
    """
    # Lê o conteúdo do arquivo em memória uma única vez
    pdf_bytes = pdf_file.read()
    
    original_name = os.path.splitext(pdf_file.name)[0]
    # Gera um nome de arquivo de saída único para evitar conflitos
    converted_filename = f"{original_name}_{uuid.uuid4().hex[:6]}.docx"
    converted_path = os.path.join(output_dir, converted_filename)

    conversion_success = False
    error_message = ""

    # --- TENTATIVA 1: Conversão Direta com pdf2docx ---
    try:
        # pdf2docx pode precisar de um arquivo, então o criamos temporariamente
        temp_pdf_path = os.path.join(output_dir, f"temp_{uuid.uuid4()}.pdf")
        with open(temp_pdf_path, 'wb') as temp_f:
            temp_f.write(pdf_bytes)
            
        cv = Converter(temp_pdf_path)
        cv.convert(converted_path, start=0, end=None)
        cv.close()

        # Limpa o arquivo temporário
        os.remove(temp_pdf_path)
        
        # Verifica se o arquivo foi criado e tem um tamanho razoável
        if os.path.exists(converted_path) and os.path.getsize(converted_path) > 100: # Tamanho mínimo para um docx
            conversion_success = True
            
    except Exception as e:
        error_message = f"Conversão direta falhou: {str(e)}"
        # Se o arquivo temporário ainda existir, remove
        if 'temp_pdf_path' in locals() and os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

    # --- TENTATIVA 2: OCR (se a primeira falhar) ---
    if not conversion_success:
        try:
            # Usa a versão 'convert_from_bytes' para não precisar salvar o arquivo de novo
            images = convert_from_bytes(pdf_bytes)
            doc = Document()
            
            full_text = ""
            for img in images:
                # O ideal é usar o idioma português para OCR
                text = pytesseract.image_to_string(img, lang='por')
                full_text += text + "\n\n"
            
            doc.add_paragraph(full_text)
            doc.save(converted_path)
            
            if os.path.exists(converted_path) and os.path.getsize(converted_path) > 50:
                conversion_success = True
                
        except Exception as e:
            error_message += f" | OCR também falhou: {str(e)}"

    if conversion_success:
        return True, converted_filename, ""
    else:
        # Se tudo falhou, remove o arquivo de saída vazio, se existir
        if os.path.exists(converted_path):
            os.remove(converted_path)
        return False, "", error_message