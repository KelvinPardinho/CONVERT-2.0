import os
import uuid
from PIL import Image
from typing import List, Tuple, Any

def process_image_to_pdf(
    image_files: List[Any],
    output_dir: str
) -> Tuple[bool, str, str, dict]:
    """
    Converte uma lista de arquivos de imagem em um único arquivo PDF.

    Args:
        image_files (List[Any]): Uma lista de objetos de arquivo de imagem enviados.
        output_dir (str): O diretório para salvar o PDF combinado.

    Returns:
        Tuple[bool, str, str, dict]: (sucesso, mensagem, nome_do_arquivo_pdf, dados_extras)
    """
    if not image_files:
        return False, "Nenhuma imagem foi enviada.", "", None

    try:
        # Abre a primeira imagem para iniciar o processo
        first_image_pil = Image.open(image_files[0]).convert("RGB")

        # Coleta as imagens restantes
        other_images_pil = []
        for img_file in image_files[1:]:
            img = Image.open(img_file).convert("RGB")
            other_images_pil.append(img)
        
        # Gera um nome de arquivo único para a saída
        output_filename = f"images_to_pdf_{uuid.uuid4().hex[:6]}.pdf"
        output_path = os.path.join(output_dir, output_filename)

        # Salva o PDF
        first_image_pil.save(
            output_path,
            save_all=True,
            append_images=other_images_pil
        )

        return True, f"{len(image_files)} imagens convertidas para PDF com sucesso!", output_filename, None

    except Exception as e:
        return False, f"Ocorreu um erro ao converter as imagens: {str(e)}", "", None