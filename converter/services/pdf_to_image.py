import os
import io
import uuid
import zipfile
import fitz  # PyMuPDF
from typing import List, Tuple

def convert_pdf_to_images(
    pdf_file: object,
    output_dir: str,
    image_format: str = 'png',
    rotations: List[int] = None
) -> Tuple[bool, str, str]:
    """
    Converte as páginas de um PDF em arquivos de imagem e as compacta em um .zip.

    Args:
        pdf_file (UploadedFile): O objeto de arquivo PDF enviado.
        output_dir (str): O diretório para salvar o arquivo zip.
        image_format (str): O formato da imagem de saída ('png' ou 'jpg').
        rotations (List[int]): Lista de ângulos de rotação para cada página.

    Returns:
        Tuple[bool, str, str]: (sucesso, mensagem, nome_do_arquivo_zip)
    """
    try:
        # Lê o PDF em memória
        pdf_bytes = pdf_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        base_filename = os.path.splitext(pdf_file.name)[0]
        zip_filename = f"{base_filename}_{uuid.uuid4().hex[:6]}.zip"
        zip_path = os.path.join(output_dir, zip_filename)

        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
            for i, page in enumerate(doc):
                # Aplica a rotação se fornecida
                rotation_angle = rotations[i] if rotations and i < len(rotations) else 0
                page.set_rotation(rotation_angle)

                # Renderiza a página para um pixmap (imagem em memória)
                pix = page.get_pixmap()
                
                # Converte o pixmap para bytes no formato desejado
                image_bytes = pix.tobytes(output=image_format)
                
                image_filename_in_zip = f"{base_filename}_page_{i + 1}.{image_format}"
                
                # Adiciona a imagem em bytes diretamente ao arquivo zip
                zipf.writestr(image_filename_in_zip, image_bytes)
        
        doc.close()
        return True, "PDF convertido para imagens com sucesso!", zip_filename

    except Exception as e:
        return False, f"Ocorreu um erro ao converter para imagem: {str(e)}", ""