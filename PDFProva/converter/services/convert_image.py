# services/convert_image.py (VERSÃO CORRIGIDA)

import os
import uuid
from PIL import Image
from typing import Tuple

def process_convert_image(
    image_file: object,
    target_format: str,
    rotation_angle: int,
    output_dir: str
) -> Tuple[bool, str, str, dict]:
    """
    Converte o formato de uma imagem, aplicando uma rotação.
    """
    try:
        img = Image.open(image_file)

        # <<< CORREÇÃO PRINCIPAL AQUI >>>
        # Padroniza o nome do formato para o que a Pillow espera.
        save_format = target_format.upper()
        if save_format == 'JPG':
            save_format = 'JPEG'

        # Garante que a imagem esteja no modo RGB se for salvar como JPEG
        if img.mode != 'RGB' and save_format == 'JPEG':
            img = img.convert('RGB')
        
        # Aplica a rotação
        if rotation_angle != 0:
            img = img.rotate(rotation_angle, expand=True)
            
        # Gera o nome do arquivo de saída
        original_name = os.path.splitext(image_file.name)[0]
        output_filename = f"{original_name}_{uuid.uuid4().hex[:6]}.{target_format.lower()}"
        output_path = os.path.join(output_dir, output_filename)

        # Salva a imagem usando o formato padronizado 'JPEG'
        img.save(output_path, format=save_format)
        img.close()

        return True, "Imagem convertida com sucesso!", output_filename, None

    except Exception as e:
        return False, f"Ocorreu um erro ao converter a imagem: {str(e)}", "", None